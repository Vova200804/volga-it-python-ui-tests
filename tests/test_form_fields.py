import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.form_fields_page import FormFieldsPage


@pytest.mark.form_fields
@allure.epic("Practice Automation")
@allure.feature("Form Fields — требование задания")
class TestFormFields:
    @allure.story("Список Automation Tools и поле Message")
    @allure.title("Automation Tools перенесены в Message")
    @allure.description("Список инструментов считывается Selenium и вводится в Message через запятую.")
    def test_read_tools_with_selenium_and_fill_message(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        with allure.step("Прочитать элементы Automation Tools средствами Selenium"):
            tools = page.automation_tools()
        with allure.step('Проверить: Список инструментов считывается Selenium и вводится в Message через запятую.'):
            assert tools == ["Selenium", "Playwright", "Cypress", "Appium", "Katalon Studio"]
        message = ", ".join(tools)
        with allure.step("Ввести имена инструментов в Message через запятую"):
            field = page.message()
            field.clear()
            field.send_keys(message)
        with allure.step('Проверить: Список инструментов считывается Selenium и вводится в Message через запятую.'):
            assert page.message().get_attribute("value") == (
                "Selenium, Playwright, Cypress, Appium, Katalon Studio"
            )

    @allure.story("Позитивные сценарии")
    @allure.title("Имя в основной форме обязательно")
    @allure.description("Поле имени имеет HTML-атрибут required.")
    def test_name_field_is_required(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        with allure.step('Проверить: Поле имени имеет HTML-атрибут required.'):
            assert page.driver.find_element(By.ID, "name-input").get_attribute("required") is not None

    @allure.story("Позитивные сценарии")
    @allure.title("Пароль скрывается полем password")
    @allure.description("Поле пароля отображается и имеет тип password.")
    def test_password_field_uses_password_input(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        with allure.step('Проверить: Поле пароля отображается и имеет тип password.'):
            assert page.driver.find_element(By.CSS_SELECTOR, "#feedbackForm input[type=password]").is_displayed()

    @allure.story("Позитивные сценарии")
    @allure.title("Можно выбрать несколько напитков")
    @allure.description("Два флажка напитков одновременно остаются выбранными.")
    def test_drink_checkboxes_allow_multiple_values(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        water = page.driver.find_element(By.ID, "drink1")
        coffee = page.driver.find_element(By.ID, "drink3")
        water.click()
        coffee.click()
        with allure.step('Проверить: Два флажка напитков одновременно остаются выбранными.'):
            assert water.is_selected() and coffee.is_selected()

    @allure.story("Позитивные сценарии")
    @allure.title("В группе цветов выбран только один вариант")
    @allure.description("Выбор второго цвета снимает отметку с первого.")
    def test_color_radio_group_allows_one_selection(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        page.driver.find_element(By.ID, "color1").click()
        page.driver.find_element(By.ID, "color2").click()
        with allure.step('Проверить: Выбор второго цвета снимает отметку с первого.'):
            assert page.driver.find_element(By.ID, "color2").is_selected()
            assert not page.driver.find_element(By.ID, "color1").is_selected()

    @allure.story("Позитивные сценарии")
    @allure.title("Список предпочтения содержит ожидаемые варианты")
    @allure.description("В выпадающем списке доступны предусмотренные варианты ответа.")
    def test_automation_preference_select_has_expected_options(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        select = page.driver.find_element(By.ID, "automation")
        options = [option.text for option in select.find_elements(By.TAG_NAME, "option")]
        with allure.step('Проверить: В выпадающем списке доступны предусмотренные варианты ответа.'):
            assert options == ["", "Yes", "No", "Undecided"]

    @allure.story("Позитивные сценарии")
    @allure.title("Выбор предпочтения меняет значение списка")
    @allure.description("При выборе Yes значение элемента становится yes.")
    def test_selecting_automation_preference_updates_value(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        page.driver.find_element(By.ID, "automation").send_keys("Yes")
        with allure.step('Проверить: При выборе Yes значение элемента становится yes.'):
            assert page.driver.find_element(By.ID, "automation").get_attribute("value") == "yes"

    @allure.story("Негативные сценарии")
    @allure.title("Пустое имя блокирует отправку формы")
    @allure.description("Нажатие Submit при пустом имени не отправляет форму и не показывает подтверждение.")
    def test_empty_name_is_blocked_by_required_constraint(self, open_page):
        page = FormFieldsPage(open_page("form-fields"))
        name = page.driver.find_element(By.ID, "name-input")
        page.submit_button().click()
        with allure.step('Проверить: Нажатие Submit при пустом имени не отправляет форму и не показывает подтверждение.'):
            assert page.driver.execute_script("return arguments[0].validity.valueMissing", name) is True
            assert page.driver.execute_script("return arguments[0].checkValidity()", name) is False
            assert not EC.alert_is_present()(page.driver)

