from django.test import TestCase

from ..conf import settings


class VocabAppConfigTest(TestCase):

    def test_defaults(self):
        self.assertEqual('profile', settings.USERS_URL_PREFIX)
        self.assertEqual(100, settings.USERS_IMAGE_DEFAULT_SIZE)
        self.assertEqual(1024 * 1024, settings.USERS_IMAGE_MAX_SIZE)
        self.assertEqual('images/default-profile.jpg', settings.USERS_IMAGE_DEFAULT_URL)
        self.assertFalse(settings.USERS_USE_GRAVATAR)
        self.assertEqual('https://www.gravatar.com/avatar/', settings.USERS_GRAVATAR_BASE_URL)
        self.assertEqual('https://www.gravatar.com', settings.USERS_GRAVATAR_CHANGE_URL)
        self.assertEqual('identicon', settings.USERS_GRAVATAR_DEFAULT)
