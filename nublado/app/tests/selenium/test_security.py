from django.contrib.auth import get_user_model

from .base import FunctionalTest, page_titles, links, error_msgs, DEFAULT_PWD

User = get_user_model()

links.update({
    "login_link_en": "Log in",
    "logout_link_en": "Log out",
})

error_msgs.update({
    "login_error_en": "Invalid login"
})


class LoginTest(FunctionalTest):

    def setUp(self):
        super(LoginTest, self).setUp()
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@cfs.com",
            password=DEFAULT_PWD
        )

    def test_login_user(self):
        # Open login page from home page.
        self.browser.get(self.live_server_url)
        login_link = self.get_login_link()
        self.assertIn(links["login_link_en"], login_link.text)
        login_link.click()

        # Invalid data
        self.login_user(
            username=self.user.username,
            password="{}77".format(DEFAULT_PWD)
        )
        form = self.get_element_by_id("login-form")
        self.assertIn(error_msgs["login_error_en"], form.text)

        # Valid data and redirection
        self.login_user(
            password=DEFAULT_PWD
        )
        self.assertIn(page_titles["user_login_redirect_en"], self.browser.title)
        self.logout_user()
        self.assertIn(page_titles["home_en"], self.browser.title)
        login_link = self.get_login_link()
        self.assertIn(links["login_link_en"], login_link.text)
