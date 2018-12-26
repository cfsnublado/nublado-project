from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Backs up a project\'s sources as json files.'

    def add_arguments(self, parser):
        parser.add_argument('output_path', nargs='+', type=str)

    def handle(self, *args, **options):
        pass
