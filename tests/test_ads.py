import allure
import pytest
from selenium.webdriver.common.by import By

from pages.ads_page import AdsPage


@pytest.mark.ads
@allure.epic("Practice Automation")
@allure.feature("Ads")
class TestAds:
    @allure.story("Позитивные сценарии")
    @allure.title("Страница Ads открывается")
    @allure.description("После открытия страницы виден заголовок Ads.")
    @allure.step("Выполнить сценарий: Страница Ads открывается")
    def test_page_heading_is_ads(self, open_page):
        assert AdsPage(open_page("ads")).heading() == "Ads"

    @allure.story("Позитивные сценарии")
    @allure.title("Страница сообщает о задержке рекламы")
    @allure.description("Основной текст страницы объясняет, что реклама появится с задержкой.")
    @allure.step("Выполнить сценарий: Страница сообщает о задержке рекламы")
    def test_page_explains_delayed_ad(self, open_page):
        page = AdsPage(open_page("ads"))
        assert "An ad will appear in 5" in page.driver.find_element(By.ID, "main").text

    @allure.story("Позитивные сценарии")
    @allure.title("Реклама появляется после задержки")
    @allure.description("Время активации рекламы попадает в ожидаемый интервал от начала навигации.")
    @allure.step("Выполнить сценарий: Реклама появляется после задержки")
    def test_ad_appears_after_delay(self, open_page):
        page = AdsPage(open_page("ads"))
        with allure.step("Сверить записанное время активации с диапазоном от 4 до 12 секунд после навигации"):
            ad, elapsed = page.wait_for_ad_after(earliest_seconds=4, timeout=12)
        assert ad.is_displayed()
        assert 4 <= elapsed <= 12

    @allure.story("Позитивные сценарии")
    @allure.title("Реклама показывает заголовок и текст")
    @allure.description("В появившейся рекламе видны ожидаемые заголовок и содержимое.")
    @allure.step("Выполнить сценарий: Реклама показывает заголовок и текст")
    def test_ad_has_expected_title_and_content(self, open_page):
        page = AdsPage(open_page("ads"))
        ad = page.wait_for_ad()
        assert ad.find_element(By.CSS_SELECTOR, ".pum-title").text.strip() == "Hi"
        assert "I am an ad." in ad.text

    @allure.story("Позитивные сценарии")
    @allure.title("У рекламы есть доступная кнопка закрытия")
    @allure.description("Кнопка закрытия видима, активна и имеет доступное имя.")
    @allure.step("Выполнить сценарий: У рекламы есть доступная кнопка закрытия")
    def test_ad_has_close_button(self, open_page):
        page = AdsPage(open_page("ads"))
        ad = page.wait_for_ad()
        close = ad.find_element(By.CSS_SELECTOR, ".pum-close")
        assert close.is_displayed() and close.is_enabled()
        assert close.get_attribute("aria-label") == "Close"

    @allure.story("Позитивные сценарии")
    @allure.title("Кнопка закрывает рекламу")
    @allure.description("После нажатия на крестик рекламная модалка исчезает.")
    @allure.step("Выполнить сценарий: Кнопка закрывает рекламу")
    def test_ad_close_button_dismisses_ad(self, open_page):
        page = AdsPage(open_page("ads"))
        page.close_ad()
        assert not page.driver.find_element(*page.AD).is_displayed()

    @allure.story("Позитивные сценарии")
    @allure.title("Рекламный диалог связан с заголовком")
    @allure.description("Диалог имеет роль dialog и корректную ссылку aria-labelledby.")
    @allure.step("Выполнить сценарий: Рекламный диалог связан с заголовком")
    def test_ad_dialog_has_valid_accessible_title_reference(self, open_page):
        page = AdsPage(open_page("ads"))
        ad = page.wait_for_ad()
        assert ad.get_attribute("role") == "dialog"
        title_id = ad.get_attribute("aria-labelledby")
        assert title_id
        assert page.driver.find_element(By.ID, title_id).text.strip() == "Hi"

    @allure.story("Негативные сценарии")
    @allure.title("Реклама не появляется раньше срока")
    @allure.description("До минимального порога реклама ещё не активирована.")
    @allure.step("Выполнить сценарий: Реклама не появляется раньше срока")
    def test_ad_is_not_activated_before_delay_threshold(self, open_page):
        page = AdsPage(open_page("ads"))
        page.wait_until_navigation_elapsed(4)
        activation = page.ad_activation_elapsed()
        assert activation is None or activation >= 4

    @allure.story("Негативные сценарии")
    @allure.title("Щелчок по тексту не закрывает рекламу")
    @allure.description("После щелчка по содержимому рекламное окно остаётся открытым.")
    @allure.step("Выполнить сценарий: Щелчок по тексту не закрывает рекламу")
    def test_clicking_ad_content_does_not_dismiss_modal(self, open_page):
        page = AdsPage(open_page("ads"))
        ad = page.wait_for_ad()
        ad.find_element(By.CSS_SELECTOR, ".pum-content").click()
        assert ad.is_displayed()

    @allure.story("Негативные сценарии")
    @allure.title("Закрытие рекламы сохраняет страницу")
    @allure.description("Реклама исчезает, а URL и основной заголовок страницы сохраняются.")
    @allure.step("Выполнить сценарий: Закрытие рекламы сохраняет страницу")
    def test_close_dismisses_ad_and_preserves_page(self, open_page):
        page = AdsPage(open_page("ads"))
        original = page.driver.current_url
        page.close_ad()
        assert not page.driver.find_element(*page.AD).is_displayed()
        assert page.driver.current_url == original
        assert page.driver.find_element(By.CSS_SELECTOR, "h1").is_displayed()
