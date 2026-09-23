import allure
import pytest
from selenium.webdriver.common.by import By

from pages.modals_page import ModalsPage


@pytest.mark.modals
@allure.epic("Practice Automation")
@allure.feature("Modals")
class TestModals:
    @allure.story("Позитивные сценарии")
    @allure.title("Страница Modals открывается")
    @allure.description("После открытия страницы виден заголовок Modals.")
    @allure.step("Выполнить сценарий: Страница Modals открывается")
    def test_page_heading_is_modals(self, open_page):
        assert ModalsPage(open_page("modals")).heading() == "Modals"

    @allure.story("Позитивные сценарии")
    @allure.title("Кнопка простой модалки доступна")
    @allure.description("Кнопка открытия простой модалки активна.")
    @allure.step("Выполнить сценарий: Кнопка простой модалки доступна")
    def test_page_exposes_simple_modal_trigger(self, open_page):
        page = ModalsPage(open_page("modals"))
        assert page.driver.find_element(*page.SIMPLE_TRIGGER).is_enabled()

    @allure.story("Позитивные сценарии")
    @allure.title("Кнопка модалки с формой доступна")
    @allure.description("Кнопка открытия модалки с формой активна.")
    @allure.step("Выполнить сценарий: Кнопка модалки с формой доступна")
    def test_page_exposes_form_modal_trigger(self, open_page):
        page = ModalsPage(open_page("modals"))
        assert page.driver.find_element(*page.FORM_TRIGGER).is_enabled()

    @allure.story("Позитивные сценарии")
    @allure.title("Простая модалка показывает заголовок и текст")
    @allure.description("После открытия модалки видны ожидаемые заголовок и содержимое.")
    @allure.step("Выполнить сценарий: Простая модалка показывает заголовок и текст")
    def test_simple_modal_shows_expected_title_and_copy(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_simple()
        assert modal.find_element(By.CSS_SELECTOR, ".pum-title").text == "Simple Modal"
        assert "Hi, I’m a simple modal." in modal.text

    @allure.story("Позитивные сценарии")
    @allure.title("У простой модалки есть кнопка закрытия")
    @allure.description("Кнопка закрытия модалки видима и активна.")
    @allure.step("Выполнить сценарий: У простой модалки есть кнопка закрытия")
    def test_simple_modal_has_close_control(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_simple()
        close = modal.find_element(By.CSS_SELECTOR, ".pum-close")
        assert close.is_displayed() and close.is_enabled()

    @allure.story("Позитивные сценарии")
    @allure.title("Кнопка закрывает простую модалку")
    @allure.description("После нажатия кнопки закрытия модалка исчезает.")
    @allure.step("Выполнить сценарий: Кнопка закрывает простую модалку")
    def test_simple_modal_closes_with_button(self, open_page):
        page = ModalsPage(open_page("modals"))
        page.close(page.open_simple())
        assert not page.driver.find_element(*page.SIMPLE).is_displayed()

    @allure.story("Позитивные сценарии")
    @allure.title("Модалка с формой содержит основные поля")
    @allure.description("В форме видны имя, почта, сообщение и кнопка отправки.")
    @allure.step("Выполнить сценарий: Модалка с формой содержит основные поля")
    def test_form_modal_contains_name_email_message_and_submit(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_form()
        assert modal.find_element(By.ID, "g1051-name").is_displayed()
        assert modal.find_element(By.ID, "g1051-email").is_displayed()
        assert modal.find_element(By.ID, "contact-form-comment-g1051-message").is_displayed()
        assert modal.find_element(By.CSS_SELECTOR, "button[type='submit']").is_enabled()

    @allure.story("Позитивные сценарии")
    @allure.title("Имя в модалке помечено обязательным")
    @allure.description("Поле имени имеет признаки обязательности в HTML и ARIA.")
    @allure.step("Выполнить сценарий: Имя в модалке помечено обязательным")
    def test_form_modal_marks_name_required(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_form()
        field = modal.find_element(By.ID, "g1051-name")
        assert field.get_attribute("required") == "true"
        assert field.get_attribute("aria-required") == "true"

    @allure.story("Негативные сценарии")
    @allure.title("Пустое имя вызывает ошибку формы")
    @allure.description("Попытка отправить форму без имени показывает сообщение об обязательном поле.")
    @allure.step("Выполнить сценарий: Пустое имя вызывает ошибку формы")
    def test_form_modal_shows_required_name_error(self, open_page):
        page = ModalsPage(open_page("modals"))
        page.open_form()
        with allure.step("Отправить форму без обязательного имени"):
            page.form_submit()
        assert page.driver.find_element(By.CSS_SELECTOR, "#pum-674 .contact-form__input-error").text == "This field is required."

    @allure.story("Негативные сценарии")
    @allure.title("Некорректная почта в модалке отклоняется")
    @allure.description("Браузер помечает адрес без корректного формата как невалидный.")
    @allure.step("Выполнить сценарий: Некорректная почта в модалке отклоняется")
    def test_form_modal_email_rejects_invalid_address(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_form()
        modal.find_element(By.ID, "g1051-name").send_keys("QA Test")
        email = modal.find_element(By.ID, "g1051-email")
        email.send_keys("not-an-email")
        page.form_submit()
        assert page.driver.execute_script("return arguments[0].validity.typeMismatch", email) is True
        assert page.driver.execute_script("return arguments[0].checkValidity()", email) is False

    @allure.story("Негативные сценарии")
    @allure.title("Закрытие неотправленной формы не показывает успех")
    @allure.description("При закрытии формы без отправки не появляется сообщение об успешной отправке.")
    @allure.step("Выполнить сценарий: Закрытие неотправленной формы не показывает успех")
    def test_closing_unsubmitted_form_modal_does_not_show_success(self, open_page):
        page = ModalsPage(open_page("modals"))
        modal = page.open_form()
        page.close(modal)
        assert not modal.is_displayed()
        success_messages = page.driver.find_elements(By.CSS_SELECTOR, "#pum-674 .contact-form-submission")
        assert not any(message.is_displayed() for message in success_messages)
