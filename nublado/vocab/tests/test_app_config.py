from django.test import TestCase

from ..conf import settings


class VocabAppConfigTest(TestCase):

    def test_defaults(self):
        self.assertEqual('vocab', settings.VOCAB_URL_PREFIX)
