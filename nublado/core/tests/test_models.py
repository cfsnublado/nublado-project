import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext as _

from ..managers import OrderedModelManager
from ..models import (
    AccessModel, OrderedModel, ProjectModel, ProjectMemberModel,
    SerializeModel, SlugifyModel,
    TimestampModel
)
from coretest.models import (
    TestAccessModel, TestLanguageModel, TestModel, TestOrderedModel,
    TestParentModel, TestProjectModel, TestProjectContentModel,
    TestProjectMemberModel, TestProjectPublishMemberModel,
    TestTrackedFieldModel, TestTranslationModel, TestTimestampModel,
    TestUserstampModel, TestUUIDModel
)

User = get_user_model()

# Testing abstract classes in core using test models from coretest.


class OrderedModelTest(TestCase):
    def setUp(self):
        self.foo_group = TestModel.objects.create(
            name="Test Group Container"
        )
        self.foo_a = TestOrderedModel.objects.create(
            foo_group=self.foo_group,
            name="foo A"
        )
        self.foo_b = TestOrderedModel.objects.create(
            foo_group=self.foo_group,
            name="foo B"
        )
        self.foo_c = TestOrderedModel.objects.create(
            foo_group=self.foo_group,
            name="foo C"
        )
        self.foo_d = TestOrderedModel.objects.create(
            foo_group=self.foo_group,
            name="foo D"
        )

    def test_inheritance(self):
        classes = (
            OrderedModel,
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(TestOrderedModel, class_name)
            )

    def test_order_on_create(self):
        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

    # Manager tests
    def test_manager(self):
        self.assertIsInstance(
            TestOrderedModel.objects, OrderedModelManager
        )

    def test_append_to_order(self):
        foo = TestOrderedModel(foo_group=self.foo_group, name="new foo")
        foo.save()
        self.assertEqual(foo.order, 1)
        manager = TestOrderedModel.objects
        group_filter = manager._OrderedModelManager__get_group_filter_dict(foo)
        max_order = manager._OrderedModelManager__get_max_order(group_filter)
        TestOrderedModel.objects.append_to_order(foo)
        self.assertEqual(foo.order, 5)
        self.assertEqual(foo.order, max_order + 1)

    def test_change_order(self):
        TestOrderedModel.objects.change_order(self.foo_c, 1)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_c.order, 1)
        self.assertEqual(self.foo_a.order, 2)
        self.assertEqual(self.foo_b.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        TestOrderedModel.objects.change_order(self.foo_c, 3)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        TestOrderedModel.objects.change_order(self.foo_c, 4)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_d.order, 3)
        self.assertEqual(self.foo_c.order, 4)

        TestOrderedModel.objects.change_order(self.foo_c, 1)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_c.order, 1)
        self.assertEqual(self.foo_a.order, 2)
        self.assertEqual(self.foo_b.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        TestOrderedModel.objects.change_order(self.foo_a, 3)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_c.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_a.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        TestOrderedModel.objects.change_order(self.foo_a, 1)
        TestOrderedModel.objects.change_order(self.foo_c, 3)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        # Test same order.
        TestOrderedModel.objects.change_order(self.foo_c, 3)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        # Test out of range
        TestOrderedModel.objects.change_order(self.foo_c, 0)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

        TestOrderedModel.objects.change_order(self.foo_c, 5)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

    def test_close_order_gap(self):
        self.foo_b.delete()
        TestOrderedModel.objects.close_order_gap(self.foo_b)
        self.foo_a.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_c.order, 2)
        self.assertEqual(self.foo_d.order, 3)

        self.foo_a.delete()
        TestOrderedModel.objects.close_order_gap(self.foo_a)
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_c.order, 1)
        self.assertEqual(self.foo_d.order, 2)

        self.foo_d.delete()
        TestOrderedModel.objects.close_order_gap(self.foo_d)
        self.foo_c.refresh_from_db()

        self.assertEqual(self.foo_c.order, 1)

        self.foo_c.delete()
        TestOrderedModel.objects.close_order_gap(self.foo_c)

    def test_close_order_gap_no_delete(self):
        """
        Orders are unchanged if supposedly removed element
        still exists in db

        """

        TestOrderedModel.objects.close_order_gap(self.foo_b)
        self.foo_a.refresh_from_db()
        self.foo_b.refresh_from_db()
        self.foo_c.refresh_from_db()
        self.foo_d.refresh_from_db()

        self.assertEqual(self.foo_a.order, 1)
        self.assertEqual(self.foo_b.order, 2)
        self.assertEqual(self.foo_c.order, 3)
        self.assertEqual(self.foo_d.order, 4)

    # Private functions
    def test_private_get_group_filter_dict(self):
        foo = TestOrderedModel.objects.get(order=1)
        manager = TestOrderedModel.objects
        group_filter = manager._OrderedModelManager__get_group_filter_dict(foo)
        expected_group_filter = {"foo_group_id": foo.foo_group_id}

        self.assertEqual(group_filter, expected_group_filter)

    def test_private_get_max_order(self):
        foo = TestOrderedModel.objects.get(order=1)
        manager = TestOrderedModel.objects
        group_filter = manager._OrderedModelManager__get_group_filter_dict(foo)
        max_order = manager._OrderedModelManager__get_max_order(group_filter)

        self.assertEqual(max_order, 4)


class ProjectModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password="Coffee?69c"
        )
        self.project = TestProjectModel.objects.create(
            owner=self.user,
            name="hello"
        )

    def test_inheritance(self):
        classes = (
            ProjectModel, AccessModel, TimestampModel, SlugifyModel,
            SerializeModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(TestProjectModel, class_name)
            )


class ProjectMemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password="Coffee?69c"
        )
        self.user_2 = User.objects.create_user(
            username="naranjo",
            first_name="Naranjo",
            last_name="Oranges",
            email="naranjo@foo.com",
            password="Coffee?69c"
        )
        self.project = TestProjectModel.objects.create(
            owner=self.user,
            name="hello"
        )

    def test_unique_together_member_project(self):
        member_1 = TestProjectMemberModel.objects.create(
            project=self.project,
            member=self.user_2
        )
        member_1.full_clean()

        # Attempt to create another project member with same user.
        with self.assertRaises(IntegrityError):
            member_2 = TestProjectMemberModel.objects.create(
                project=self.project,
                member=self.user_2
            )
            member_2.full_clean()

    def test_new_member_not_owner(self):
        member_1 = TestProjectMemberModel.objects.create(
            project=self.project,
            member=self.user_2
        )
        member_1.full_clean()

        # Attempt to create a member from owner.
        with self.assertRaises(ValidationError):
            member_2 = TestProjectMemberModel.objects.create(
                project=self.project,
                member=self.user
            )
            member_2.full_clean()


class ProjectPublishMemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password="Coffee?69c"
        )
        self.project = TestProjectModel.objects.create(
            owner=self.user,
            name="hello"
        )

    def test_inheritance(self):
        classes = (
            ProjectMemberModel,
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(TestProjectPublishMemberModel, class_name)
            )

    def test_access_status_values(self):
        member = TestProjectPublishMemberModel.objects.create(
            project=self.project,
            member=self.user
        )
        self.assertEqual(member.ROLE_OWNER, 4)
        self.assertEqual(member.ROLE_ADMIN, 3)
        self.assertEqual(member.ROLE_EDITOR, 2)
        self.assertEqual(member.ROLE_AUTHOR, 1)

    def test_default_access_status(self):
        member = TestProjectPublishMemberModel.objects.create(
            project=self.project,
            member=self.user
        )
        self.assertEqual(member.role, TestProjectPublishMemberModel.ROLE_AUTHOR)


class ProjectContentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password="Coffee?69c"
        )
        self.project = TestProjectModel.objects.create(
            owner=self.user,
            name="hello"
        )
        self.project_content = TestProjectContentModel.objects.create(
            creator=self.user,
            name="hello",
            content="asdf asdf"
        )

    def test_get_project(self):
        project = self.project_content.get_project()
        self.assertEqual("foo", project)


class AccessModelTest(TestCase):

    def setUp(self):
        self.test_model = TestAccessModel.objects.create(name="hello")

    def test_access_status_values(self):
        self.assertEqual(TestAccessModel.ACCESS_PUBLIC, 3)
        self.assertEqual(TestAccessModel.ACCESS_PROTECTED, 2)
        self.assertEqual(TestAccessModel.ACCESS_PRIVATE, 1)

    def test_default_access_status(self):
        self.assertEqual(self.test_model.access_status, TestAccessModel.ACCESS_PUBLIC)


class TrackedFieldModelTest(TestCase):

    def setUp(self):
        self.test_model = TestTrackedFieldModel.objects.create(name="hello")

    def test_field_changed(self):
        self.assertEqual(TestTrackedFieldModel.tracked_fields, ["name"])

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
        self.test_model = TestParentModel.objects.create(name="hello")
        self.test_model_2 = TestParentModel.objects.create(
            name="hello",
            parent=self.test_model
        )
        self.test_model_3 = TestParentModel.objects.create(
            name="hello",
            parent=self.test_model
        )

    def test_parent_objects(self):
        objects = TestParentModel.objects.all()
        self.assertEqual(3, len(objects))
        parents = TestParentModel.objects.parents.all()
        self.assertEqual(1, len(parents))

    def test_children_related_name_property(self):
        self.assertEqual(
            "coretest_testparentmodel_children",
            TestParentModel.objects.children_related_name
        )

    def test_is_parent_property(self):
        self.assertTrue(self.test_model.is_parent)
        self.assertFalse(self.test_model_2.is_parent)
        self.assertFalse(self.test_model_3.is_parent)


class TranslationModelTest(TestCase):
    def setUp(self):
        self.test_model_en = TestTranslationModel.objects.create(
            language="en",
        )
        self.test_model_es = TestTranslationModel.objects.create(
            language="es",
            parent=self.test_model_en
        )

    def test_get_available_languages(self):
        languages = self.test_model_en.get_available_languages()
        self.assertEqual((("en", _("English")),), languages)
        languages = self.test_model_en.get_available_languages(include_self_language=False)
        self.assertEqual((), languages)
        languages = self.test_model_en.get_available_languages(include_self_language=True)
        self.assertEqual((("en", _("English")),), languages)
        self.assertNotIn("fr", dict(self.test_model_en.LANGUAGE_CHOICES))
        languages = self.test_model_en.get_available_languages(exceptions=["es", "fr"])
        self.assertEqual((("en", _("English")), ("es", _("Spanish"))), languages)

    def test_get_translation(self):
        translation = self.test_model_en.get_translation("es")
        self.assertEqual(translation, self.test_model_es)
        translation = self.test_model_en.get_translation("fr")
        self.assertIsNone(translation)
        translation = self.test_model_en.get_translation("cham")
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
            username="ale7",
            first_name="Alejandra",
            last_name="Acosta",
            email="ale7@foo.com",
            password="Coffee?69c"
        )
        self.test_model = TestUserstampModel.objects.create(name="hello")

    def test_save(self):
        self.test_model.created_by = self.user
        self.test_model.last_updated_by = self.user
        self.test_model.save()
        self.assertEqual(self.test_model.created_by, self.user)
        self.assertEqual(self.test_model.last_updated_by, self.user)


class UUIDModelTest(TestCase):
    def setUp(self):
        self.test_model = TestUUIDModel.objects.create(name="hello")

    def test_id_is_uuid(self):
        self.assertIsInstance(self.test_model.id, uuid.UUID)

    def test_pk_is_uuid(self):
        self.assertIsInstance(self.test_model.pk, uuid.UUID)
        self.assertEqual(self.test_model.pk, self.test_model.id)

    def test_set_uuid_on_create(self):
        test_id = uuid.uuid4()
        test_model = TestUUIDModel.objects.create(id=test_id, name="hello")
        self.assertEqual(test_model.id, test_id)


class TimestampModelTest(TestCase):

    def test_datetime_on_create_and_update(self):
        test_model = TestTimestampModel.objects.create(name="hello")
        created = test_model.date_created
        updated = test_model.date_updated
        self.assertEqual(
            (created.year, created.month, created.day, created.hour, created.minute),
            (updated.year, updated.month, updated.day, updated.hour, updated.minute)
        )
        test_model.name = "good bye"
        test_model.save()
        self.assertGreater(test_model.date_updated, updated)

    def test_date_created_provided_on_create(self):
        date_created = timezone.now() + timezone.timedelta(hours=-48, minutes=-1, seconds=-1)
        test_model = TestTimestampModel.objects.create(
            name="hello",
            date_created=date_created
        )
        self.assertEqual(test_model.date_created, date_created)
        self.assertGreater(test_model.date_updated, test_model.date_created)


class LanguageModelTest(TestCase):

    def setUp(self):
        self.test_model_en = TestLanguageModel.objects.create(name="hello", language="en")
        self.test_model_es = TestLanguageModel.objects.create(name="hola", language="es")

    def test_default_language_is_app_settings_default_langauge(self):
        test_model = TestLanguageModel.objects.create(name="foo")
        self.assertEqual(settings.LANGUAGE_CODE, test_model.language)

    def test_validation_language_not_in_language_choices(self):
        with self.assertRaises(ValidationError):
            self.test_model_en.language = "xx"
            self.test_model_en.full_clean()
