from __future__ import annotations

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class AdsPage(BasePage):
    AD = (By.ID, "pum-1272")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("Дождаться появления рекламного окна")
    def wait_for_ad(self):
        ad = self.wait.until(EC.visibility_of_element_located(self.AD))
        self.wait.until(EC.visibility_of(ad.find_element(By.CSS_SELECTOR, ".pum-title")))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#pum-1272 .pum-close")))
        return ad

    @allure.step("Измерить появление рекламы после {earliest_seconds} секунд")
    def wait_for_ad_after(self, earliest_seconds: float, timeout: float = 12):
        """Return the ad and its measured activation time from navigation start."""
        if earliest_seconds < 0 or timeout <= earliest_seconds:
            raise ValueError("Require 0 <= earliest_seconds < timeout")
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.1)

        def appeared_after_delay(driver):
            activation_ms = driver.execute_script(
                "return window.__practiceAdActivationMs ?? null"
            )
            if activation_ms is None:
                return False
            elapsed = activation_ms / 1000
            if elapsed < earliest_seconds:
                raise AssertionError(
                    f"Ad appeared too early ({elapsed:.2f}s; expected >= {earliest_seconds:.2f}s)"
                )
            if elapsed > timeout:
                raise AssertionError(
                    f"Ad appeared too late ({elapsed:.2f}s; expected <= {timeout:.2f}s)"
                )
            active = driver.find_elements(By.CSS_SELECTOR, "#pum-1272.pum-active")
            return (active[0], elapsed) if active and active[0].is_displayed() else False

        return wait.until(appeared_after_delay)

    def ad_activation_elapsed(self) -> float | None:
        activation_ms = self.driver.execute_script(
            "return window.__practiceAdActivationMs ?? null"
        )
        return activation_ms / 1000 if activation_ms is not None else None

    def wait_until_navigation_elapsed(self, seconds: float) -> None:
        WebDriverWait(self.driver, seconds + 1, poll_frequency=0.1).until(
            lambda driver: driver.execute_script("return performance.now()") / 1000 >= seconds
        )

    @allure.step("Закрыть рекламное окно")
    def close_ad(self):
        ad = self.wait_for_ad()
        ad.find_element(By.CSS_SELECTOR, ".pum-close").click()
        self.wait.until(EC.invisibility_of_element(ad))
