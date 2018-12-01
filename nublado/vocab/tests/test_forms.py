from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext as _

from ..forms import (
    VocabContextCreateForm, VocabEntryCreateForm,
    VocabSourceCreateForm
)
from ..models import VocabSource

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

    def test_create_source(self):
        form = VocabEntryCreateForm(
            data=self.vocab_entry_data,
            creator=self.user
        )
        vocab_entry = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(vocab_entry.creator, self.user)
        self.assertEqual(vocab_entry.entry, self.vocab_entry_data["entry"])
        self.assertEqual(vocab_entry.language, self.vocab_entry_data["language"])

    def test_form_error_if_no_creator(self):
        with self.assertRaisesRegexp(ValueError, _("validation_vocab_content_creator_required")):
            VocabEntryCreateForm(data=self.vocab_entry_data)


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
            creator=self.user,
            vocab_source=self.source
        )
        context = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(context.vocab_source, self.source)
        self.assertEqual(context.content, self.context_data["content"])

    def test_form_error_if_no_source(self):
        with self.assertRaisesRegexp(ValueError, _("validation_vocab_source_required")):
            VocabContextCreateForm(data=self.context_data, creator=self.user)

