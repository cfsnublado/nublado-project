from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext as _

from ..forms import (
    VocabContextCreateForm, VocabEntryCreateForm,
    VocabContextAudioCreateForm, VocabSourceCreateForm
)
from ..models import VocabContext, VocabSource

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )


class VocabEntryCreateFormTest(TestCommon):

    def setUp(self):
        super(VocabEntryCreateFormTest, self).setUp()
        self.vocab_entry_data = {
            "language": "en",
            "entry": "Hello",
        }

    def test_create_entry(self):
        form = VocabEntryCreateForm(
            data=self.vocab_entry_data
        )
        vocab_entry = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(vocab_entry.entry, self.vocab_entry_data["entry"])
        self.assertEqual(vocab_entry.language, self.vocab_entry_data["language"])


class VocabSourceCreateFormTest(TestCommon):

    def setUp(self):
        super(VocabSourceCreateFormTest, self).setUp()
        self.source_data = {
            "source_type": VocabSource.CREATED,
            "name": "Test source",
            "description": "A test source"
        }

    def test_create_source(self):
        form = VocabSourceCreateForm(
            data=self.source_data,
            creator=self.user
        )
        source = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(source.creator, self.user)
        self.assertEqual(source.name, self.source_data["name"])
        self.assertEqual(source.description, self.source_data["description"])

    def test_form_error_if_no_creator(self):
        with self.assertRaisesRegexp(ValueError, _("validation_vocab_content_creator_required")):
            VocabSourceCreateForm(data=self.source_data)


class VocabContextCreateFormTest(TestCommon):

    def setUp(self):
        super(VocabContextCreateFormTest, self).setUp()
        self.source = VocabSource.objects.create(
            creator=self.user,
            name="Test source"
        )
        self.context_data = {
            "content": "This is some content."
        }

    def test_create_context(self):
        form = VocabContextCreateForm(
            data=self.context_data,
            vocab_source=self.source
        )
        context = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(context.vocab_source, self.source)
        self.assertEqual(context.content, self.context_data["content"])

    def test_form_error_if_no_source(self):
        with self.assertRaisesRegexp(ValueError, _("validation_vocab_source_required")):
            VocabContextCreateForm(data=self.context_data)


class VocabContextAudioCreateFormTest(TestCommon):

    def setUp(self):
        super(VocabContextAudioCreateFormTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content"
        )
        self.vocab_context_audio_data = {
            "name": "Test audio",
            "audio_url": "https://www.foo.com/foo.mp3"
        }

    def test_create_vocab_context_audio(self):
        form = VocabContextAudioCreateForm(
            data=self.vocab_context_audio_data,
            creator=self.user,
            vocab_context=self.vocab_context
        )
        vocab_context_audio = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(vocab_context_audio.creator, self.user)
        self.assertEqual(vocab_context_audio.vocab_context, self.vocab_context)
        self.assertEqual(vocab_context_audio.name, self.vocab_context_audio_data["name"])
        self.assertEqual(vocab_context_audio.audio_url, self.vocab_context_audio_data["audio_url"])

    def test_form_error_if_no_creator(self):
        with self.assertRaisesRegexp(ValueError, _("validation_creator_required")):
            VocabContextAudioCreateForm(
                data=self.vocab_context_audio_data,
                vocab_context=self.vocab_context
            )

    def test_form_error_if_no_vocab_context(self):
        with self.assertRaisesRegexp(ValueError, _("validation_vocab_context_required")):
            VocabContextAudioCreateForm(
                data=self.vocab_context_audio_data,
                creator=self.user
            )