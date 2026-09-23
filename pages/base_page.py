from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 12, poll_frequency=0.2)

    def heading(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(("css selector", "h1"))).text
