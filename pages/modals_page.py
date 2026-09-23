from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class ModalsPage(BasePage):
    SIMPLE_TRIGGER = (By.ID, "simpleModal")
    FORM_TRIGGER = (By.ID, "formModal")
    SIMPLE = (By.ID, "pum-1318")
    FORM = (By.ID, "pum-674")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def open_simple(self):
        self.wait.until(EC.element_to_be_clickable(self.SIMPLE_TRIGGER)).click()
        modal = self.wait.until(EC.visibility_of_element_located(self.SIMPLE))
        self.wait.until(EC.visibility_of(modal.find_element(By.CSS_SELECTOR, ".pum-title")))
        return modal

    def open_form(self):
        self.wait.until(EC.element_to_be_clickable(self.FORM_TRIGGER)).click()
        modal = self.wait.until(EC.visibility_of_element_located(self.FORM))
        self.wait.until(EC.visibility_of(modal.find_element(By.CSS_SELECTOR, ".pum-title")))
        return modal

    def close(self, modal):
        modal.find_element(By.CSS_SELECTOR, ".pum-close").click()
        self.wait.until(EC.invisibility_of_element(modal))

    def form_submit(self):
        self.driver.find_element(By.CSS_SELECTOR, "#pum-674 button[type='submit']").click()
