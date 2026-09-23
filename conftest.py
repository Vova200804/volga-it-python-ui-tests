from __future__ import annotations

import os
from pathlib import Path

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

ROOT = Path(__file__).resolve().parent
FAILURE_DIR = ROOT / "artifacts" / "failures"
AD_ACTIVATION_OBSERVER = r"""
(() => {
  const markActivation = () => {
    const modal = document.getElementById("pum-1272");
    if (modal?.classList.contains("pum-active") && window.__practiceAdActivationMs == null) {
      window.__practiceAdActivationMs = performance.now();
    }
  };
  new MutationObserver(markActivation).observe(document, {
    subtree: true, childList: true, attributes: true, attributeFilter: ["class"]
  });
  markActivation();
})();
"""


@pytest.fixture(scope="session", autouse=True)
def prepare_failure_artifacts() -> None:
    FAILURE_DIR.mkdir(parents=True, exist_ok=True)
    for old_screenshot in FAILURE_DIR.glob("*.png"):
        old_screenshot.unlink(missing_ok=True)


@pytest.fixture
def driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--lang=en-US")
    if os.getenv("HEADLESS", "1") != "0":
        options.add_argument("--headless=new")
    binary = os.getenv("CHROME_BINARY")
    if binary:
        options.binary_location = binary
    driver_path = os.getenv("CHROMEDRIVER")
    service = Service(driver_path) if driver_path else Service()
    browser = webdriver.Chrome(options=options, service=service)
    browser.set_page_load_timeout(45)
    browser.set_script_timeout(20)
    browser.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": AD_ACTIVATION_OBSERVER},
    )
    try:
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def open_page(driver: webdriver.Chrome):
    def open_url(path: str) -> webdriver.Chrome:
        url = f"https://practice-automation.com/{path.strip('/')}/"
        with allure.step(f"Открыть страницу {url}"):
            driver.get(url)
        return driver

    return open_url


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when not in {"setup", "call"} or not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return
    FAILURE_DIR.mkdir(parents=True, exist_ok=True)
    screenshot = FAILURE_DIR / f"{item.nodeid.replace('::', '_').replace('/', '_')}.png"
    try:
        browser.save_screenshot(str(screenshot))
        allure.attach.file(
            str(screenshot),
            name="Скриншот при ошибке",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            browser.current_url,
            name="URL при ошибке",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception as error:  # retain original assertion failure
        report.sections.append(("screenshot capture", repr(error)))
