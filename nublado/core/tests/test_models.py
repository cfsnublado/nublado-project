import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext as _

from coretest.models import (
    TestLanguageModel, TestParentModel, TestTrackedFieldModel,
    TestTranslationModel, TestTimestampModel, TestUserstampModel,
    TestUUIDModel
)

User = get_user_model()

# Testing abstract classes in core using test models from coretest.


class TrackedFieldModelTest(TestCase):

    def setUp(self):
        self.test_model = TestTrackedFieldModel.objects.create(name="hello")

    def test_field_changed(self):
        self.test_model.name = "hello"
        self.assertFalse(self.test_model.field_changed("name"))
        self.test_model.name = "something"
        self.assertTrue(self.test_model.field_changed("name"))
        self.test_model.save()
        self.assertFalse(self.test_model.field_changed("name"))
        self.test_model.name = "hello"
        self.assertTrue(self.test_model.field_changed("name"))


class ParentModelTest(TestCase):
    def setUp(self):
        self.test_model = TestParentModel.objects.create(name='hello')
        self.test_model_2 = TestParentModel.objects.create(
            name='hello',
            parent=self.test_model
        )
        self.test_model_3 = TestParentModel.objects.create(
            name='hello',
            parent=self.test_model
        )

    def test_parent_objects(self):
        objects = TestParentModel.objects.all()
        self.assertEqual(3, len(objects))
        parents = TestParentModel.objects.parents.all()
        self.assertEqual(1, len(parents))

    def test_children_related_name_property(self):
        self.assertEqual(
            'coretest_testparentmodel_children',
            TestParentModel.objects.children_related_name
        )

    def test_is_parent_property(self):
        self.assertTrue(self.test_model.is_parent)
        self.assertFalse(self.test_model_2.is_parent)
        self.assertFalse(self.test_model_3.is_parent)


class TranslationModelTest(TestCase):
    def setUp(self):
        self.test_model_en = TestTranslationModel.objects.create(
            language='en',
        )
        self.test_model_es = TestTranslationModel.objects.create(
            language='es',
            parent=self.test_model_en
        )

    def test_get_available_languages(self):
        languages = self.test_model_en.get_available_languages()
        self.assertEqual((('en', _('English')),), languages)
        languages = self.test_model_en.get_available_languages(include_self_language=False)
        self.assertEqual((), languages)
        languages = self.test_model_en.get_available_languages(include_self_language=True)
        self.assertEqual((('en', _('English')),), languages)
        self.assertNotIn('fr', dict(self.test_model_en.LANGUAGE_CHOICES))
        languages = self.test_model_en.get_available_languages(exceptions=['es', 'fr'])
        self.assertEqual((('en', _('English')), ('es', _('Spanish'))), languages)

    def test_get_translation(self):
        translation = self.test_model_en.get_translation('es')
        self.assertEqual(translation, self.test_model_es)
        translation = self.test_model_en.get_translation('fr')
        self.assertIsNone(translation)
        translation = self.test_model_en.get_translation('cham')
        self.assertIsNone(translation)
        translation = self.test_model_en.get_translation(None)
        self.assertIsNone(translation)

    def test_translations_property(self):
        translations = TestTranslationModel.objects.translations
        self.assertEqual(len(translations), 1)
        self.assertEqual(translations[0], self.test_model_es)


class UserstampModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestUserstampModel.objects.create(name='hello')

    def test_save(self):
        self.test_model.created_by = self.user
        self.test_model.last_updated_by = self.user
        self.test_model.save()
        self.assertEqual(self.test_model.created_by, self.user)
        self.assertEqual(self.test_model.last_updated_by, self.user)


class UUIDModelTest(TestCase):
    def setUp(self):
        self.test_model = TestUUIDModel.objects.create(name='hello')

    def test_id_is_uuid(self):
        self.assertIsInstance(self.test_model.id, uuid.UUID)

    def test_pk_is_uuid(self):
        self.assertIsInstance(self.test_model.pk, uuid.UUID)
        self.assertEqual(self.test_model.pk, self.test_model.id)

    def test_set_uuid_on_create(self):
        test_id = uuid.uuid4()
        test_model = TestUUIDModel.objects.create(id=test_id, name='hello')
        self.assertEqual(test_model.id, test_id)


class TimestampModelTest(TestCase):

    def test_datetime_on_create_and_update(self):
        test_model = TestTimestampModel.objects.create(name='hello')
        created = test_model.date_created
        updated = test_model.date_updated
        self.assertEqual(
            (created.year, created.month, created.day, created.hour, created.minute),
            (updated.year, updated.month, updated.day, updated.hour, updated.minute)
        )
        test_model.name = 'good bye'
        test_model.save()
        self.assertGreater(test_model.date_updated, updated)

    def test_date_created_provided_on_create(self):
        date_created = timezone.now() + timezone.timedelta(hours=-48, minutes=-1, seconds=-1)
        test_model = TestTimestampModel.objects.create(
            name='hello',
            date_created=date_created
        )
        self.assertEqual(test_model.date_created, date_created)
        self.assertGreater(test_model.date_updated, test_model.date_created)


class LanguageModelTest(TestCase):

    def setUp(self):
        self.test_model_en = TestLanguageModel.objects.create(name='hello', language='en')
        self.test_model_es = TestLanguageModel.objects.create(name='hola', language='es')

    def test_default_language_is_app_settings_default_langauge(self):
        test_model = TestLanguageModel.objects.create(name='foo')
        self.assertEqual(settings.LANGUAGE_CODE, test_model.language)

    def test_validation_language_not_in_language_choices(self):
        with self.assertRaises(ValidationError):
            self.test_model_en.language = 'xx'
            self.test_model_en.full_clean()
