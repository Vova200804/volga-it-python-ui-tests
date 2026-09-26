from datetime import date

import allure
import pytest
from selenium.webdriver.common.keys import Keys
from pages.calendar_page import CalendarPage


def _next_leap_day(after: date) -> date:
    year = after.year
    while True:
        try:
            leap_day = date(year, 2, 29)
        except ValueError:
            year += 1
            continue
        if leap_day > after:
            return leap_day
        year += 1


@pytest.mark.calendars
@allure.epic("Practice Automation")
@allure.feature("Calendars")
class TestCalendars:
    @allure.story("Позитивные сценарии")
    @allure.title("Страница Calendars открывается")
    @allure.description("После открытия страницы виден заголовок Calendars.")
    def test_page_heading_is_calendars(self, open_page):
        with allure.step("Открыть календарь"):
            page = CalendarPage(open_page("calendars"))
        with allure.step('Проверить: После открытия страницы виден заголовок Calendars.'):
            assert page.heading() == "Calendars"

    @allure.story("Позитивные сценарии")
    @allure.title("Поле даты имеет подпись и подсказку формата")
    @allure.description("Подпись связана с полем даты, а подсказка показывает формат YYYY-MM-DD.")
    def test_date_field_has_label_and_format_hint(self, open_page):
        page = CalendarPage(open_page("calendars"))
        field = page.field()
        label = page.driver.find_element("css selector", "#main label.grunion-field-label.date")
        format_hint = page.driver.find_element("css selector", "#main .contact-form__field-format")
        with allure.step('Проверить: Подпись связана с полем даты, а подсказка показывает формат YYYY-MM-DD.'):
            assert label.is_displayed()
            assert label.text.strip() == "Select or enter a date"
            assert label.get_attribute("for") == field.get_attribute("id")
            assert format_hint.is_displayed()
            assert format_hint.text.strip() == "YYYY-MM-DD"

    @allure.story("Позитивные сценарии")
    @allure.title("Щелчок по дате открывает календарь")
    @allure.description("При щелчке по полю даты календарь становится видимым.")
    def test_clicking_field_opens_calendar(self, open_page):
        page = CalendarPage(open_page("calendars"))
        with allure.step("Открыть виджет выбора даты"):
            page.open_picker()
        with allure.step('Проверить: При щелчке по полю даты календарь становится видимым.'):
            assert page.driver.find_element(*page.PICKER).is_displayed()

    @allure.story("Позитивные сценарии")
    @allure.title("Календарь показывает месяц, год и навигацию")
    @allure.description("В открытом календаре доступны текущие месяц и год, а также кнопки перехода.")
    def test_calendar_exposes_month_and_year_navigation(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.open_picker()
        with allure.step('Проверить: В открытом календаре доступны текущие месяц и год, а также кнопки перехода.'):
            assert page.driver.find_element("css selector", ".dp-cal-month").text
            assert page.driver.find_element("css selector", ".dp-cal-year").text.isdigit()
            assert page.driver.find_element("css selector", ".dp-prev").is_displayed()
            assert page.driver.find_element("css selector", ".dp-next").is_displayed()

    @allure.story("Позитивные сценарии")
    @allure.title("Навигация переключает месяц вперёд и назад")
    @allure.description("Переход вперёд меняет месяц, а возврат восстанавливает исходный месяц.")
    def test_next_and_previous_month_controls_work(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.open_picker()
        initial = (page.driver.find_element("css selector", ".dp-cal-month").text, page.driver.find_element("css selector", ".dp-cal-year").text)
        with allure.step("Перейти на следующий месяц и вернуться назад"):
            page.driver.find_element("css selector", ".dp-next").click()
            after_next = (page.driver.find_element("css selector", ".dp-cal-month").text, page.driver.find_element("css selector", ".dp-cal-year").text)
            page.driver.find_element("css selector", ".dp-prev").click()
        with allure.step('Проверить: Переход вперёд меняет месяц, а возврат восстанавливает исходный месяц.'):
            assert after_next != initial
            assert (page.driver.find_element("css selector", ".dp-cal-month").text, page.driver.find_element("css selector", ".dp-cal-year").text) == initial

    @allure.story("Позитивные сценарии")
    @allure.title("Можно выбрать дату следующего месяца")
    @allure.description("Выбор дня следующего месяца записывает правильную дату в поле.")
    def test_select_date_in_next_month(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.open_picker()
        current_month = page.displayed_month()
        next_month_number = current_month.month % 12 + 1
        next_month_year = current_month.year + (current_month.month == 12)
        target = date(next_month_year, next_month_number, 14)
        with allure.step(f"Выбрать дату {target.isoformat()} через календарь"):
            chosen = page.choose(target)
        with allure.step('Проверить: Выбор дня следующего месяца записывает правильную дату в поле.'):
            assert chosen == target.isoformat()

    @allure.story("Позитивные сценарии")
    @allure.title("Можно выбрать дату следующего года")
    @allure.description("Выбор дня того же месяца следующего года записывает правильную дату.")
    def test_select_date_in_next_year(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.open_picker()
        current_month = page.displayed_month()
        target = date(current_month.year + 1, current_month.month, 5)
        with allure.step(f"Выбрать дату {target.isoformat()} через календарь"):
            chosen = page.choose(target)
        with allure.step('Проверить: Выбор дня того же месяца следующего года записывает правильную дату.'):
            assert chosen == target.isoformat()

    @allure.story("Позитивные сценарии")
    @allure.title("Можно выбрать 29 февраля високосного года")
    @allure.description("Календарь позволяет выбрать следующий високосный день и записывает его в поле.")
    def test_calendar_selects_leap_day(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.open_picker()
        current_month = page.displayed_month()
        leap_day = _next_leap_day(current_month)
        with allure.step('Проверить: Календарь позволяет выбрать следующий високосный день и записывает его в поле.'):
            assert page.choose(leap_day) == leap_day.isoformat()

    @allure.story("Позитивные сценарии")
    @allure.title("Корректная дата принимается без ошибки")
    @allure.description("Дата формата YYYY-MM-DD остаётся в поле и не вызывает ошибку валидации.")
    def test_form_accepts_well_formed_date(self, open_page):
        page = CalendarPage(open_page("calendars"))
        page.field().send_keys("2026-12-31", Keys.TAB)
        with allure.step('Проверить: Дата формата YYYY-MM-DD остаётся в поле и не вызывает ошибку валидации.'):
            assert page.field().get_attribute("value") == "2026-12-31"
            assert page.field().get_attribute("data-format") == "yy-mm-dd"
            assert page.field().get_attribute("aria-invalid") != "true"
            assert page.field_error() == ""

    @allure.story("Позитивные сценарии")
    @allure.title("Выбранная дата успешно отправляется")
    @allure.description("После выбора корректной даты и отправки формы появляется подтверждение.")
    def test_selected_date_can_be_submitted(self, open_page):
        page = CalendarPage(open_page("calendars"))
        with allure.step("Ввести корректную дату"):
            page.field().send_keys("2026-12-31", Keys.TAB)
        with allure.step("Проверить успешную отправку"):
            assert page.submit_and_wait_for_success().startswith("Thank you for your response.")

    @allure.story("Негативные сценарии")
    @pytest.mark.parametrize("value", ["not-a-date", "2026-02-30", "2026/10/14"], ids=["text", "impossible-day", "wrong-format"])
    @allure.title("Некорректная дата отклоняется")
    @allure.description("Текст, несуществующий день или неверный формат вызывают сообщение об ошибке.")
    def test_invalid_date_is_rejected_with_inline_error(self, open_page, value):
        page = CalendarPage(open_page("calendars"))
        with allure.step(f"Ввести нестандартное значение {value}"):
            error = page.enter_invalid_date(value)
        with allure.step('Проверить: Текст, несуществующий день или неверный формат вызывают сообщение об ошибке.'):
            assert error == "Please enter a valid date."

    @allure.story("Негативные сценарии")
    @allure.title("Ошибка даты исчезает после исправления")
    @allure.description("После замены неверной даты корректной поле больше не помечено ошибочным.")
    def test_date_value_can_be_corrected(self, open_page):
        page = CalendarPage(open_page("calendars"))
        field = page.field()
        field.send_keys("2026-02-30", Keys.TAB)
        page.wait.until(lambda _: field.get_attribute("aria-invalid") == "true")
        page.wait.until(lambda _: page.field_error() == "Please enter a valid date.")
        field.clear()
        field.send_keys("2026-12-31", Keys.TAB)
        page.wait.until(lambda _: field.get_attribute("aria-invalid") != "true")
        page.wait.until(lambda _: page.field_error() == "")
        with allure.step('Проверить: После замены неверной даты корректной поле больше не помечено ошибочным.'):
            assert page.field().get_attribute("value") == "2026-12-31"
            assert page.field_error() == ""
