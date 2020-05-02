import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

from core.management.base import LoginCommand
from vocab.models import VocabEntry
from vocab.utils import export_vocab_entries


class Command(LoginCommand):
    help = 'Backs up the vocab entries in a json file.'

    def add_arguments(self, parser):
        parser.add_argument('--output_path', nargs=1, type=str)

    def handle(self, *args, **options):
        user = self.login_user()
        if not user.is_superuser:
            raise CommandError('Superuser required')

        languages = VocabEntry.LANGUAGE_CHOICES

        if options['output_path']:
            base_dir = Path(options['output_path'][0])
        else:
            base_dir = Path('{0}/docs/vocab_json/entries'.format(settings.BASE_DIR))
        base_dir.mkdir(parents=True, exist_ok=True)

        for language in languages:
            language_key = language[0]
            vocab_entries_dict = export_vocab_entries(language=language_key)
            entries_dir = base_dir / language_key
            entries_dir.mkdir(parents=True, exist_ok=True)
            filename = entries_dir / 'vocab_entries.json'

            with filename.open('w+') as f:
                f.write(json.dumps(vocab_entries_dict, indent=2))
                self.stdout.write(self.style.SUCCESS(filename))
