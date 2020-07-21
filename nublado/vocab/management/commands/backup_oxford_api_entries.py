import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

from core.management.base import LoginCommand
from vocab.models import VocabEntry, VocabEntryJsonData


class Command(LoginCommand):
    help = "Backs up Oxford API vocab entry data."

    def add_arguments(self, parser):
        parser.add_argument("--output_path", nargs=1, type=str)

    def handle(self, *args, **options):
        user = self.login_user()
        if not user.is_superuser:
            raise CommandError("Superuser required")

        languages = VocabEntry.LANGUAGE_CHOICES

        if options["output_path"]:
            base_dir = Path(options["output_path"][0])
        else:
            base_dir = Path("{0}/docs/vocab_json/oxford_api".format(settings.BASE_DIR))
        base_dir.mkdir(parents=True, exist_ok=True)

        for language in languages:
            language_key = language[0]

            vocab_entries_json = VocabEntryJsonData.objects.filter(
                json_data_source=VocabEntryJsonData.OXFORD,
                vocab_entry__language=language_key
            ).select_related("vocab_entry")

            entries_json_dir = base_dir / language_key
            entries_json_dir.mkdir(parents=True, exist_ok=True)

            for vocab_entry_json in vocab_entries_json.all():
                filename = entries_json_dir / "{0}.json".format(vocab_entry_json.vocab_entry.slug)

                with filename.open("w+") as f:
                    f.write(json.dumps(vocab_entry_json.json_data, indent=2))
                    self.stdout.write(self.style.SUCCESS(filename))
