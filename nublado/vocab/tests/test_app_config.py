from django.test import TestCase

from ..conf import settings


class VocabAppConfigTest(TestCase):

    def test_defaults(self):
        self.assertEqual("vocab", settings.VOCAB_URL_PREFIX)
        self.assertEqual(
            settings.BASE_DIR.child("docs", "vocab_backup", "entries"),
            settings.VOCAB_ENTRIES_BACKUP_DIR
        )
        self.assertEqual(
            settings.BASE_DIR.child("docs", "vocab_backup", "sources"),
            settings.VOCAB_SOURCES_BACKUP_DIR
        )
