from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

DEFAULT_WAIT = 3
PROJECT_NAME = "Nublado"
DEFAULT_PWD = "Pizza?69p"

msgs = {
    "msg_success_en": "Success",
    "msg_error_en": "Error",
}

error_msgs = {
    "field_required": "This field is required."
}

page_titles = {
    "home_en": "{0} | {1}".format("Home", PROJECT_NAME),
    "user_login_redirect_en": "{0} | {1}".format("Home", PROJECT_NAME),
    "login_en": "{0} | {1}".format("Log in", PROJECT_NAME),
}

links = {}


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)
        self.wait = WebDriverWait(self.browser, 10)

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

    def select_language_from_language_changer(self, language="en"):
        self.get_element_by_id("language-changer").click()
        self.get_element_by_css("#" + language).click()

    def get_user_toggle(self):
        return self.get_element_by_id("navbar-user-dropdown")

    def get_login_link(self):
        return self.get_element_by_class("login-link")

    def get_logout_link(self):
        return self.get_element_by_class("logout-link")

    def get_messages(self):
        return self.get_element_by_id("messages")

    def get_top_messages(self):
        return self.get_element_by_id("top-messages")

    def get_submit_button(self):
        return self.get_element_by_xpath('//*[@type="submit"]')

    def get_element_by_id(self, id):
        return self.browser.find_element_by_id(id)

    def get_element_by_class(self, class_name):
        return self.browser.find_element_by_class_name(class_name)

    def get_element_by_css(self, css_selector):
        return self.browser.find_element_by_css_selector(css_selector)

    def get_element_by_link_text(self, link_text):
        return self.browser.find_element_by_link_text(link_text)

    def get_element_by_tag_name(self, tag_name):
        return self.browser.find_element_by_tag_name(tag_name)

    def get_element_by_xpath(self, xpath):
        return self.browser.find_element_by_xpath(xpath)

    def get_elements_by_xpath(self, xpath):
        return self.browser.find_elements_by_xpath(xpath)

    def login_user(self, username=None, password=None):
        self.load_page(page_titles["login_en"])

        if username is not None:
            self.get_element_by_id("username").send_keys(username)

        if password is not None:
            self.get_element_by_id("password").send_keys(password)
        else:
            self.get_element_by_id("password").send_keys(DEFAULT_PWD)

        self.get_submit_button().click()

    def logout_user(self):
        self.get_user_toggle().click()
        self.get_logout_link().click()

    def open_sidebar(self):
        self.get_element_by_id("navbar-sidebar-trigger").click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "sidebar-language-selector")))

    def close_sidebar(self):
        self.get_element_by_id("sidebar-trigger").click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, "sidebar")))

    def open_modal(self, trigger_id=None, modal_id=None):
        self.get_element_by_id(trigger_id).click()
        self.wait.until(EC.visibility_of_element_located((By.ID, modal_id)))

    def click_modal_background(self):
        outside = self.get_element_by_id("modal-background")
        action = webdriver.common.action_chains.ActionChains(self.browser)
        action.move_to_element_with_offset(outside, 10, 10)
        action.click()
        action.perform()

    def load_page(self, page_title):
        self.wait.until(EC.title_contains(page_title))

    def search_click(self, search_text=None, search_btn_id="search-btn"):
        search_input = self.get_element_by_id("search-input")
        search_input.clear()
        search_input.send_keys(search_text)
        search_btn = self.get_element_by_id(search_btn_id)
        search_btn.click()

    def search_click_by_language(
        self, search_text=None, language="en", search_btn_id="search-btn"
    ):
        language_id = "search-language-{0}".format(language)
        language_switcher = self.get_element_by_id("search-language")
        language_switcher.click()
        self.wait.until(EC.element_to_be_clickable((By.ID, language_id)))
        self.get_element_by_id(language_id).click()
        self.search_click(search_text=search_text, search_btn_id=search_btn_id)

    def search_autocomplete(self, search_text=None, autocomplete_text=None):
        search_input = self.get_element_by_id("search-input")
        search_input.clear()
        search_input.send_keys(search_text)

        if autocomplete_text is None:
            autocomplete_text = search_text

        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, autocomplete_text)))

        return self.get_element_by_link_text(autocomplete_text)

    def search_autocomplete_by_language(self, language="en", search_text=None, autocomplete_text=None):
        language_id = "search-language-{0}".format(language)
        language_switcher = self.get_element_by_id("search-language")
        language_switcher.click()
        self.wait.until(EC.element_to_be_clickable((By.ID, language_id)))
        self.get_element_by_id(language_id).click()
        result_link = self.search_autocomplete(search_text=search_text, autocomplete_text=autocomplete_text)

        return result_link
