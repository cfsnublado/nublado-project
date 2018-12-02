from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from core.models import (
    LanguageModel, SerializeModel,
    SlugifyModel, TimestampModel, TrackedFieldModel
)
from ..managers import VocabEntryManager, VocabProjectManager, VocabSourceManager
from ..models import (
    CreatorModel, VocabProject, VocabSourceContentModel, VocabEntry,
    VocabContext, VocabContextEntry, VocabSource
)
from ..serializers import (
    VocabEntrySerializer, VocabContextEntrySerializer, VocabContextSerializer,
    VocabProjectSerializer, VocabSourceSerializer
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@cfs.com',
            password=self.pwd
        )


class VocabProjectTest(TestCommon):

    def setUp(self):
        super(VocabProjectTest, self).setUp()

        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='Test project',
            description='A test project'
        )

    def test_inheritance(self):
        classes = (
            SerializeModel, SlugifyModel,
            TimestampModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabProject, class_name)
            )

    def test_manager_type(self):
        self.assertIsInstance(VocabEntry.objects, VocabEntryManager)

    def test_string_representation(self):
        self.assertEqual(str(self.vocab_project), self.vocab_project.name)

    def test_unique_together_owner_name(self):
        user_2 = User.objects.create_user(
            username='val',
            first_name='Val',
            last_name='Val',
            email='val7@val.com',
            password=self.pwd
        )
        name = 'Project'
        vocab_project_1 = VocabProject.objects.create(
            owner=self.user,
            name=name
        )
        vocab_project_1.full_clean()
        vocab_project_2 = VocabProject.objects.create(
            owner=user_2,
            name=name
        )
        vocab_project_2.full_clean()
        with self.assertRaises(IntegrityError):
            vocab_project_3 = VocabProject.objects.create(
                owner=user_2,
                name=name
            )
            vocab_project_3.full_clean()

    def test_get_serializer(self):
        serializer = self.vocab_project.get_serializer()
        self.assertEqual(serializer, VocabProjectSerializer)


class VocabEntryTest(TestCommon):

    def setUp(self):
        super(VocabEntryTest, self).setUp()

        self.vocab_entry = VocabEntry.objects.create(
            entry='vertiginoso',
            description='me gusta esta palabra',
            language='es',
        )

    def test_inheritance(self):
        classes = (
            LanguageModel, SerializeModel, SlugifyModel,
            TimestampModel, TrackedFieldModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabEntry, class_name)
            )

    def test_manager_type(self):
        self.assertIsInstance(VocabProject.objects, VocabProjectManager)

    def test_string_representation(self):
        self.assertEqual(str(self.vocab_entry), self.vocab_entry.entry)

    def test_unique_together_entry_language(self):
        entry = 'inextricable'
        vocab_entry_1 = VocabEntry.objects.create(entry=entry, language='en')
        vocab_entry_1.full_clean()
        vocab_entry_2 = VocabEntry.objects.create(entry=entry, language='es')
        vocab_entry_2.full_clean()
        with self.assertRaises(IntegrityError):
            vocab_entry_5 = VocabEntry.objects.create(entry=entry, language='en')
            vocab_entry_5.full_clean()

    # def test_entry_lowercase_on_save(self):
    #     self.vocab_entry.entry = 'Darse Cuenta de'
    #     self.vocab_entry.full_clean()
    #     self.vocab_entry.save()
    #     self.assertEqual('darse cuenta de', self.vocab_entry.entry)

    def test_update_slug_on_save(self):
        self.vocab_entry.entry = 'darse cuenta de'
        self.vocab_entry.full_clean()
        self.vocab_entry.save()
        self.assertEqual('darse-cuenta-de', self.vocab_entry.slug)

    def test_get_serializer(self):
        serializer = self.vocab_entry.get_serializer()
        self.assertEqual(serializer, VocabEntrySerializer)


class VocabContextTest(TestCommon):

    def setUp(self):
        super(VocabContextTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test_project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            source_type=VocabSource.CREATED,
            name='Test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='''Tergiversar. Hay que tergiversar el mensaje.
                ¡Tergivérsalo! Pero no lo tergiverses demasiado. Demasiado sería no solo confuso, sino devastador.
                Al tergiversar el mensaje, ten cuidado de no tergiversarlo demasiado.
                Demasiada tergiversación no es buena.''',
        )

    def test_inheritance(self):
        classes = (
            VocabSourceContentModel, SerializeModel,
            TimestampModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabContext, class_name)
            )

    def test_get_vocab_source(self):
        vocab_source = self.vocab_context.get_vocab_source()
        self.assertEqual(vocab_source, self.vocab_source)

    def test_get_serializer(self):
        serializer = self.vocab_context.get_serializer()
        self.assertEqual(serializer, VocabContextSerializer)


class VocabContextEntryTest(TestCommon):

    def setUp(self):
        super(VocabContextEntryTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test_project'
        )
        self.vocab_entry = VocabEntry.objects.create(
            entry='vertiginoso',
            description='vertiginosamente bien',
            language='es'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            source_type=VocabSource.CREATED,
            name='Created source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='''Tergiversar. Hay que tergiversar el mensaje.
                ¡Tergivérsalo! Pero no lo tergiverses demasiado. Demasiado sería no solo confuso, sino devastador.
                Al tergiversar el mensaje, ten cuidado de no tergiversarlo demasiado.
                Demasiada tergiversación no es buena.''',
        )
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context,
        )
        self.vocab_context_entry.add_vocab_entry_tag('tergiversar')
        self.vocab_context_entry.add_vocab_entry_tag('tergiverses')
        self.vocab_context_entry.add_vocab_entry_tag('tergiversarlo')

    def test_inheritance(self):
        classes = (
            VocabSourceContentModel, SerializeModel,
            TimestampModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabContextEntry, class_name)
            )

    def test_get_vocab_entry_tags(self):
        tags = self.vocab_context_entry.get_vocab_entry_tags()
        tags_2 = ['tergiverses', 'tergiversarlo', 'tergiversar']
        tags_2.sort()
        self.assertEqual(tags, tags_2)
        self.assertEqual(tags, ['tergiversar', 'tergiversarlo', 'tergiverses'])

    def test_vocab_entry_not_deleted(self):
        entry_id = self.vocab_entry.id
        context_id = self.vocab_context.id
        entry = self.vocab_entry.entry
        self.vocab_context.delete()
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_entry_id=entry_id,
                vocab_context_id=context_id
            ).exists()
        )
        self.assertTrue(VocabEntry.objects.filter(entry=entry).exists())

    def test_get_vocab_source(self):
        vocab_source = self.vocab_context_entry.get_vocab_source()
        self.assertEqual(vocab_source, self.vocab_source)

    def test_get_serializer(self):
        serializer = self.vocab_context_entry.get_serializer()
        self.assertEqual(serializer, VocabContextEntrySerializer)


class VocabSourceTest(TestCommon):

    def setUp(self):
        super(VocabSourceTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test_project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Some book',
            description='A good book',
            source_type=VocabSource.BOOK,
        )

    def test_inheritance(self):
        classes = (
            SerializeModel, SlugifyModel,
            TimestampModel, CreatorModel
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabSource, class_name)
            )

    def test_manager_type(self):
        self.assertIsInstance(VocabSource.objects, VocabSourceManager)

    def test_string_representation(self):
        self.assertEqual(str(self.vocab_source), self.vocab_source.name)

    def test_unique_together_project_name(self):
        source_name_1 = 'A reading test source'
        source_name_2 = 'Another reading test source'
        vocab_source_1 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name=source_name_1
        )
        vocab_source_1.full_clean()
        vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name=source_name_2
        )
        vocab_source_2.full_clean()
        with self.assertRaises(IntegrityError):
            vocab_entry_3 = VocabSource.objects.create(
                vocab_project=self.vocab_project,
                creator=self.user,
                name=source_name_1
            )
            vocab_entry_3.full_clean()

    def test_update_slug_on_save(self):
        self.vocab_source.name = 'El nombre del viento'
        self.vocab_source.full_clean()
        self.vocab_source.save()
        self.assertEqual('el-nombre-del-viento', self.vocab_source.slug)

    def test_get_serializer(self):
        serializer = self.vocab_source.get_serializer()
        self.assertEqual(serializer, VocabSourceSerializer)
