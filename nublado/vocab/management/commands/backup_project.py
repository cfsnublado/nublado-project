import getpass
import json
import os

from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand, CommandError

from vocab.models import VocabProject
from vocab.utils import export_vocab_source


class Command(BaseCommand):
    help = 'Backs up a project\'s sources as json files.'

    def login_user(self):
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        user = authenticate(username=username, password=password)

        if user is not None:
            return user
        else:
            raise CommandError('Invalid login')

    def add_arguments(self, parser):
        parser.add_argument('output_path', nargs=1, type=str)

    def handle(self, *args, **options):
        user = self.login_user()

        vocab_projects = VocabProject.objects.filter(owner=user)
        for vocab_project in vocab_projects:
            vocab_sources = vocab_project.vocab_sources.all()
            for vocab_source in vocab_sources:
                vocab_source_dict = export_vocab_source(vocab_source=vocab_source)
                file_path = os.path.join(options['output_path'][0], vocab_source.slug)

                with open(file_path, 'w+') as f:
                    f.write(json.dumps(vocab_source_dict, indent=2))
