from __future__ import annotations

import calendar
from datetime import date

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class CalendarPage(BasePage):
    FIELD = (By.CSS_SELECTOR, "#main input.jp-contact-form-date")
    PICKER = (By.CSS_SELECTOR, ".dp-cal")
    SUBMIT = (By.CSS_SELECTOR, "#main form.contact-form button[type='submit']")
    SUCCESS = (By.CSS_SELECTOR, "#main .contact-form-submission.submission-success h4")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def field(self):
        return self.wait.until(EC.visibility_of_element_located(self.FIELD))

    @allure.step("Открыть виджет выбора даты")
    def open_picker(self):
        field = self.field()
        def open_when_ready(driver):
            visible = [picker for picker in driver.find_elements(*self.PICKER) if picker.is_displayed()]
            if visible:
                return visible[0]
            field.click()
            return False

        self.wait.until(open_when_ready)
        return field

    def displayed_month(self) -> date:
        month_name = self.driver.find_element(By.CSS_SELECTOR, ".dp-cal-month").text
        year = int(self.driver.find_element(By.CSS_SELECTOR, ".dp-cal-year").text)
        return date(year, list(calendar.month_name).index(month_name), 1)

    @allure.step("Выбрать дату {target} в календаре")
    def choose(self, target: date) -> str:
        field = self.field()
        visible_pickers = self.driver.find_elements(*self.PICKER)
        if not any(picker.is_displayed() for picker in visible_pickers):
            self.open_picker()
        for _ in range(48):
            visible_month = self.driver.find_element(By.CSS_SELECTOR, ".dp-cal-month").text
            visible_year = int(self.driver.find_element(By.CSS_SELECTOR, ".dp-cal-year").text)
            visible_month_number = list(calendar.month_name).index(visible_month)
            if (visible_year, visible_month_number) == (target.year, target.month):
                break
            visible = date(visible_year, visible_month_number, 1)
            desired = date(target.year, target.month, 1)
            direction = ".dp-next" if desired > visible else ".dp-prev"
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, direction))).click()
        else:
            raise AssertionError(f"Не удалось перейти к месяцу {target:%Y-%m} за 48 шагов")
        day = target.strftime("%a %b %d %Y")
        button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".dp-day[aria-label^='{day}']"))
        )
        button.click()
        return field.get_attribute("value") or ""

    def field_error(self) -> str:
        field = self.field()
        error_id = next(
            (
                part
                for part in (field.get_attribute("aria-describedby") or "").split()
                if part.endswith("-text-error-message")
            ),
            None,
        )
        if error_id is None:
            raise AssertionError("У поля даты отсутствует ссылка на сообщение об ошибке")
        return self.driver.find_element(By.ID, error_id).text

    @allure.step("Ввести дату {value} и дождаться ошибки валидации")
    def enter_invalid_date(self, value: str) -> str:
        field = self.field()

        def error_after_input(_):
            if field.get_attribute("aria-invalid") == "true":
                return self.field_error() or False
            field.clear()
            field.send_keys(value, Keys.TAB)
            return False

        return self.wait.until(error_after_input)

    @allure.step("Отправить выбранную дату и дождаться подтверждения")
    def submit_and_wait_for_success(self) -> str:
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT)).click()
        return self.wait.until(EC.visibility_of_element_located(self.SUCCESS)).text
