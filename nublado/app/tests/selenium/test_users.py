# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# from django.conf import settings
# from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode

from users.models import User
from .base import PROJECT_NAME, FunctionalTest, error_msgs, msgs, page_titles, links, DEFAULT_PWD

NEW_PWD = "Coffee?69c"

page_titles.update({
    "user_register_en": "{0} | {1}".format("Register user", PROJECT_NAME),
    "user_register_activate_en": "{0} | {1}".format("Activate account", PROJECT_NAME),
    "user_password_reset_en": "{0} | {1}".format("Change user password", PROJECT_NAME),
    "profile_update_en": "{0} | {1}".format("Edit profile", PROJECT_NAME),
})

links.update({
    "join_now_en": "Join now!",
    "gravatar_change_en": "Edit gravatar image"
})

msgs.update({
    "user_register_confirm_en": "Thank you for registering. An email has been sent to activate your account.",
    "user_activation_success": "You're good to go"
})


class TestCommon(FunctionalTest):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.user_data = {
            "username": "cfs",
            "email": "ChristopherSanders78@gmail.com.com",
            "first_name": "christopher",
            "last_name": "Sanders",
            "password1": DEFAULT_PWD,
            "password2": DEFAULT_PWD
        }

    def fill_and_submit_user_registration_form(
        self, username=None, email=None,
        first_name=None, last_name=None, pwd1=None, pwd2=None
    ):
        if username is not None:
            username_input = self.get_element_by_id("id_username")
            username_input.clear()
            username_input.send_keys(username)
        if email is not None:
            email_input = self.get_element_by_id("id_email")
            email_input.clear()
            email_input.send_keys(email)
        if first_name is not None:
            first_name_input = self.get_element_by_id("id_first_name")
            first_name_input.clear()
            first_name_input.send_keys(first_name)
        if last_name is not None:
            last_name_input = self.get_element_by_id("id_last_name")
            last_name_input.clear()
            last_name_input.send_keys(last_name)
        if pwd1 is not None:
            pwd1_input = self.get_element_by_id("id_password1")
            pwd1_input.clear()
            pwd1_input.send_keys(pwd1)
        if pwd2 is not None:
            pwd2_input = self.get_element_by_id("id_password2")
            pwd2_input.clear()
            pwd2_input.send_keys(pwd2)
        self.get_submit_button().click()

    def fill_and_submit_password_reset_form(self, pwd, new_pwd1=None, new_pwd2=None):
        if pwd is not None:
            pwd_input = self.get_element_by_id("id_current_password")
            pwd_input.clear()
            pwd_input.send_keys(pwd)
        if new_pwd1 is not None:
            new_pwd1_input = self.get_element_by_id("id_password1")
            new_pwd1_input.clear()
            new_pwd1_input.send_keys(new_pwd1)
        if new_pwd2 is not None:
            new_pwd2_input = self.get_element_by_id("id_password2")
            new_pwd2_input.clear()
            new_pwd2_input.send_keys(new_pwd2)
        self.get_submit_button().click()


class TestUser(TestCommon):

    # def test_register_user(self):
    #     self.browser.get(self.live_server_url)
    #     self.load_page(page_titles["home_en"])
    #     # Join now button
    #     user_register_btn = self.get_element_by_id("user-register-header-button")
    #     self.assertIn(links["join_now_en"], user_register_btn.text)
    #     user_register_btn.click()
    #     self.load_page(page_titles["user_register_en"])
    #     # Invalid data
    #     self.fill_and_submit_user_registration_form(
    #         email=self.user_data["email"],
    #         first_name=self.user_data["first_name"],
    #         last_name=self.user_data["last_name"],
    #         pwd1=DEFAULT_PWD,
    #         pwd2=DEFAULT_PWD
    #     )
    #     username_errors = self.get_element_by_id("id_username-errors")
    #     self.assertIn(error_msgs["field_required"], username_errors.text)
    #     # Valid data
    #     self.fill_and_submit_user_registration_form(
    #         username=self.user_data["username"],
    #         email=self.user_data["email"],
    #         first_name=self.user_data["first_name"],
    #         last_name=self.user_data["last_name"],
    #         pwd1=DEFAULT_PWD,
    #         pwd2=DEFAULT_PWD
    #     )
    #     self.load_page(page_titles["login_en"])
    #     messages = self.get_top_messages()
    #     self.assertIn(msgs["user_register_confirm_en"], messages.get_attribute("innerHTML"))
    #     # Confirm that new, inactive user acccount was created.
    #     user = User.objects.get(username=self.user_data["username"])
    #     self.assertFalse(user.is_active)

    # def test_activate_user(self):
    #     user = User.objects.create_user(
    #         username=self.user_data["username"],
    #         email=self.user_data["email"],
    #         first_name=self.user_data["first_name"],
    #         last_name=self.user_data["last_name"],
    #         password=DEFAULT_PWD,
    #     )
    #     user.is_active = False
    #     user.save()
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     token = default_token_generator.make_token(user)
    #     # Registration activation.
    #     self.browser.get("{0}{1}".format(
    #         self.live_server_url,
    #         reverse("registration:registration_activate", kwargs={"uidb64": uid, "token": token}))
    #     )
    #     self.load_page(page_titles["user_register_activate_en"])
    #     page_header = self.get_element_by_tag_name("h1")
    #     self.assertIn(msgs["user_activation_success"], page_header.text)
    #     user.refresh_from_db()
    #     self.assertTrue(user.is_active)
    #     # Revisit the activation page and receive and error message.
    #     self.browser.get("{0}{1}".format(
    #         self.live_server_url,
    #         reverse("registration:registration_activate", kwargs={"uidb64": uid, "token": token}))
    #     )
    #     self.load_page(page_titles["user_register_activate_en"])
    #     page_header = self.get_element_by_tag_name("h1")
    #     self.assertIn(msgs["msg_error_en"], page_header.text)

    def test_change_password(self):
        user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            password=DEFAULT_PWD,
        )
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("users:user_password_reset", kwargs={"username": user.username}))
        )
        self.login_user(user.username)
        self.load_page(page_titles["user_password_reset_en"])

        # Invalid data
        self.fill_and_submit_password_reset_form(
            pwd="",
            new_pwd1=NEW_PWD,
            new_pwd2=NEW_PWD
        )

        # Valid data
        self.fill_and_submit_password_reset_form(
            pwd=DEFAULT_PWD,
            new_pwd1=NEW_PWD,
            new_pwd2=NEW_PWD
        )
        self.load_page(page_titles["login_en"])
