from __future__ import annotations

import calendar
from datetime import date

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class CalendarPage(BasePage):
    FIELD = (By.CSS_SELECTOR, "#main input.jp-contact-form-date")
    PICKER = (By.CSS_SELECTOR, ".dp-cal")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def field(self):
        return self.wait.until(EC.visibility_of_element_located(self.FIELD))

    @allure.step("Открыть виджет выбора даты")
    def open_picker(self):
        field = self.field()
        field.click()
        self.wait.until(EC.visibility_of_element_located(self.PICKER))
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
        day = target.strftime("%a %b %d %Y")
        button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".dp-day[aria-label^='{day}']"))
        )
        button.click()
        return field.get_attribute("value") or ""

    def field_error(self) -> str:
        field = self.field()
        error_id = next(
            part
            for part in (field.get_attribute("aria-describedby") or "").split()
            if part.endswith("-text-error-message")
        )
        return self.driver.find_element(By.ID, error_id).text
