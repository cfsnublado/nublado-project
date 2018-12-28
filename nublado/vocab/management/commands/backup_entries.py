import getpass
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand, CommandError

from vocab.utils import export_vocab_entries


class Command(BaseCommand):
    help = 'Backs up the vocab entries in a json file.'

    def login_user(self):
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        user = authenticate(username=username, password=password)

        if user is not None:
            return user
        else:
            raise CommandError('Invalid login')

    def add_arguments(self, parser):
        parser.add_argument('--output_path', nargs=1, type=str)

    def handle(self, *args, **options):
        user = self.login_user()
        if not user.is_superuser:
            raise CommandError('Superuser required')

        if options['output_path']:
            base_dir = Path(options['output_path'][0])
        else:
            base_dir = Path('{0}/docs/vocab_json/entries'.format(settings.BASE_DIR))
        base_dir.mkdir(parents=True, exist_ok=True)

        vocab_entries_dict = export_vocab_entries()
        filename = base_dir / 'vocab_entries.json'

        with filename.open('w+') as f:
            f.write(json.dumps(vocab_entries_dict, indent=2))
            self.stdout.write(self.style.SUCCESS(filename))
