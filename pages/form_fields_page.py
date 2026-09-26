from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class FormFieldsPage(BasePage):
    AUTOMATION_TOOLS = (
        By.XPATH,
        "//form[@id='feedbackForm']//label[normalize-space()='Automation tools']/following-sibling::ul[1]/li",
    )

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def automation_tools(self) -> list[str]:
        tools = self.wait.until(EC.visibility_of_all_elements_located(self.AUTOMATION_TOOLS))
        return [tool.text.strip() for tool in tools]

    def message(self):
        return self.wait.until(EC.visibility_of_element_located((By.ID, "message")))

    def submit_button(self):
        button = self.driver.find_element(By.ID, "submit-btn")
        self.driver.execute_script(
            "document.documentElement.style.scrollBehavior = 'auto'; "
            "arguments[0].scrollIntoView({block: 'center'});",
            button,
        )
        self.wait.until(
            lambda driver: driver.execute_script(
                "const r = arguments[0].getBoundingClientRect(); "
                "return r.top >= 0 && r.bottom <= innerHeight;",
                button,
            )
        )
        return button
