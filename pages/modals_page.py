from __future__ import annotations

import allure
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class ModalsPage(BasePage):
    SIMPLE_TRIGGER = (By.ID, "simpleModal")
    FORM_TRIGGER = (By.ID, "formModal")
    SIMPLE = (By.ID, "pum-1318")
    FORM = (By.ID, "pum-674")
    NAME = (By.CSS_SELECTOR, "#pum-674 input.name")
    EMAIL = (By.CSS_SELECTOR, "#pum-674 input.email")
    MESSAGE = (By.CSS_SELECTOR, "#pum-674 textarea")
    NAME_ERROR = (By.CSS_SELECTOR, "#pum-674 .grunion-field-name-wrap .contact-form__input-error")
    EMAIL_ERROR = (By.CSS_SELECTOR, "#pum-674 .grunion-field-email-wrap .contact-form__input-error")
    SUCCESS = (By.CSS_SELECTOR, "#pum-674 .contact-form-submission.submission-success h4")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("Открыть простое модальное окно")
    def open_simple(self):
        self.wait.until(
            lambda driver: "pum-trigger"
            in driver.find_element(*self.SIMPLE_TRIGGER).get_attribute("class")
        )
        self.wait.until(EC.element_to_be_clickable(self.SIMPLE_TRIGGER)).click()
        modal = self.wait.until(EC.visibility_of_element_located(self.SIMPLE))
        self.wait.until(EC.visibility_of(modal.find_element(By.CSS_SELECTOR, ".pum-title")))
        return modal

    @allure.step("Открыть модальное окно с формой")
    def open_form(self):
        self.wait.until(
            lambda driver: "pum-trigger"
            in driver.find_element(*self.FORM_TRIGGER).get_attribute("class")
        )
        self.wait.until(EC.element_to_be_clickable(self.FORM_TRIGGER)).click()
        modal = self.wait.until(EC.visibility_of_element_located(self.FORM))
        self.wait.until(EC.visibility_of(modal.find_element(By.CSS_SELECTOR, ".pum-title")))
        return modal

    @allure.step("Закрыть модальное окно")
    def close(self, modal):
        modal.find_element(By.CSS_SELECTOR, ".pum-close").click()
        self.wait.until(EC.invisibility_of_element(modal))

    @allure.step("Нажать кнопку отправки формы")
    def form_submit(self):
        def click_when_visible(driver):
            button = driver.find_element(By.CSS_SELECTOR, "#pum-674 button[type='submit']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            if not button.is_displayed() or not button.is_enabled():
                return False
            center_is_clear = driver.execute_script(
                "const b = arguments[0], r = b.getBoundingClientRect();"
                "const x = (r.left + r.right) / 2, y = (r.top + r.bottom) / 2;"
                "return x >= 0 && x < innerWidth && y >= 0 && y < innerHeight "
                "&& b.contains(document.elementFromPoint(x, y));",
                button,
            )
            if not center_is_clear:
                return False
            try:
                button.click()
            except ElementClickInterceptedException:
                return False
            return True

        self.wait.until(click_when_visible)

    @allure.step("Заполнить форму в модальном окне")
    def fill_form(self, name: str, email: str, message: str) -> None:
        self.wait.until(EC.visibility_of_element_located(self.NAME)).send_keys(name)
        self.wait.until(EC.visibility_of_element_located(self.EMAIL)).send_keys(email)
        self.wait.until(EC.visibility_of_element_located(self.MESSAGE)).send_keys(message)

    def visible_name_error(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.NAME_ERROR)).text

    def visible_email_error(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.EMAIL_ERROR)).text

    def success_message(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.SUCCESS)).text
