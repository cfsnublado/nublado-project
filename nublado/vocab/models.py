from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import (
    LanguageModel, SerializeModel,
    SlugifyModel, TimestampModel, TrackedFieldModel
)
from core.utils import tag_text
from .managers import (
    VocabDefinitionManager, VocabEntryManager,
    VocabProjectManager, VocabSourceManager
)


# Abstract models

class CreatorModel(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class ProjectContentModel(models.Model):

    class Meta:
        abstract = True

    def get_project(self):
        raise NotImplementedError("Method get_project needs to be implemented.")


class VocabSourceContentModel(models.Model):

    class Meta:
        abstract = True

    def get_vocab_source(self):
        raise NotImplementedError("Method get_source needs to be implemented.")


# Concrete models

class VocabProject(
    TimestampModel, SlugifyModel,
    SerializeModel
):
    unique_slug = False
    value_field_name = "name"
    max_iterations = 500

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name=_("label_name"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("label_description"),
        blank=True
    )
    slug = models.SlugField(
        verbose_name=_("label_slug"),
        max_length=255,
    )

    objects = VocabProjectManager()

    class Meta:
        unique_together = ("owner", "name")
        verbose_name = _("label_vocab_project")
        verbose_name_plural = _("label_vocab_project_plural")

    def __str__(self):
        return self.name

    def get_serializer(self):
        from .serializers import VocabProjectSerializer
        return VocabProjectSerializer


class VocabEntry(
    TimestampModel, LanguageModel, SlugifyModel,
    TrackedFieldModel, SerializeModel
):
    unique_slug = False
    value_field_name = "entry"
    max_iterations = 500
    tracked_fields = ["language", "entry"]

    entry = models.CharField(
        verbose_name=_("label_entry"),
        max_length=255,
    )
    pronunciation_spelling = models.CharField(
        verbose_name=_("label_vocab_pronunciation_spelling"),
        max_length=255,
        blank=True
    )
    pronunciation_ipa = models.CharField(
        verbose_name=_("label_vocab_pronunciation_ipa"),
        max_length=255,
        blank=True
    )
    description = models.TextField(
        verbose_name=_("label_description"),
        blank=True
    )
    slug = models.SlugField(
        verbose_name=_("label_slug"),
        max_length=255,
    )

    objects = VocabEntryManager()

    class Meta:
        unique_together = ("entry", "language")
        verbose_name = _("label_vocab_entry")
        verbose_name_plural = _("label_vocab_entry_plural")

    def __str__(self):
        return self.entry

    # def clean(self, *args, **kwargs):
    #     self.entry = self.entry.lower()

    def get_serializer(self):
        from .serializers import VocabEntrySerializer
        return VocabEntrySerializer

    def add_definition(self, vocab_definition):
        self.vocab_definitions.add(vocab_definition)


class VocabDefinition(TimestampModel, SerializeModel):
    """
    Definitions for VocabEntry.

    Note: The implementation is simple. I won't go crazy with the definition and translation models,
    as I don't want to reinvent the dictionary wheel. However, it's nice to be able to add your own definitions
    however you want. For more robust definitions, external references to dictionaries like WordReference can be provided.
    """
    NOUN = 1
    ADJECTIVE = 2
    VERB = 3
    ADVERB = 4
    EXPRESSION = 5

    DEFINITION_TYPE_CHOICES = (
        (NOUN, _("label_noun")),
        (ADJECTIVE, _("label_adjective")),
        (VERB, _("label_verb")),
        (ADVERB, _("label_adverb")),
        (EXPRESSION, _("label_expression")),
    )

    vocab_entry = models.ForeignKey(
        VocabEntry,
        related_name="vocab_definitions",
        on_delete=models.CASCADE
    )
    definition = models.TextField(
        verbose_name=_("label_definition")
    )
    definition_type = models.IntegerField(
        verbose_name=_("label_vocab_definition_type"),
        choices=DEFINITION_TYPE_CHOICES,
        default=NOUN
    )

    objects = VocabDefinitionManager()

    class Meta:
        verbose_name = _("label_vocab_definition")
        verbose_name_plural = _("label_vocab_definition_plural")

    def __str__(self):
        return self.name

    def get_serializer(self):
        from .serializers import VocabDefinitionSerializer
        return VocabDefinitionSerializer


class VocabSource(
    TimestampModel, SlugifyModel, SerializeModel,
    CreatorModel, ProjectContentModel
):
    """
    A model for vocab sources that contain the contexts.
    """
    BOOK = 1
    WEBSITE = 2
    BLOG = 3
    CREATED = 4
    SOURCE_TYPE_CHOICES = (
        (BOOK, _("label_source_book")),
        (WEBSITE, _("label_source_website")),
        (BLOG, _("label_source_blog")),
        (CREATED, _("label_source_created")),
    )
    unique_slug = False
    value_field_name = "name"
    max_iterations = 500

    vocab_project = models.ForeignKey(
        VocabProject,
        related_name="vocab_sources",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name=_("label_name"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("label_description"),
        blank=True
    )
    source_type = models.IntegerField(
        verbose_name=_("label_vocab_source_type"),
        choices=SOURCE_TYPE_CHOICES,
        default=CREATED,
    )
    slug = models.SlugField(
        verbose_name=_("label_slug"),
        max_length=255,
    )

    objects = VocabSourceManager()

    class Meta:
        unique_together = ("vocab_project", "name")
        verbose_name = _("label_vocab_source")
        verbose_name_plural = _("label_vocab_source_plural")

    def __str__(self):
        return self.name

    def get_serializer(self):
        from .serializers import VocabSourceSerializer
        return VocabSourceSerializer

    def get_project(self):
        return self.vocab_project


class VocabContext(
    TimestampModel, SerializeModel, VocabSourceContentModel
):

    vocab_source = models.ForeignKey(
        VocabSource,
        related_name="vocab_contexts",
        on_delete=models.CASCADE
    )
    vocab_entries = models.ManyToManyField(
        VocabEntry,
        through="VocabContextEntry",
        related_name="vocab_context_entry"
    )
    content = models.TextField(
        verbose_name=_("label_content"),
    )

    class Meta:
        verbose_name = _("label_vocab_context")
        verbose_name_plural = _("label_vocab_context_plural")

    def __str__(self):
        return self.content

    def get_serializer(self):
        from .serializers import VocabContextSerializer
        return VocabContextSerializer

    def get_entries_and_tags(self):
        """
        Returns a dict of all of the context's vocab entries along with their
        corresponding tags (i.e., entry instances in the context.)
        """
        entries_tags = {}
        context_entries = self.vocabcontextentry_set.all()
        for context_entry in context_entries:
            vocab_entry = context_entry.vocab_entry
            entries_tags[vocab_entry.id] = {
                "vocab_entry": {
                    "id": vocab_entry.id,
                    "entry": vocab_entry.entry,
                    "language": vocab_entry.language,
                    "slug": vocab_entry.slug
                },
                "tags": context_entry.get_vocab_entry_tags()
            }
        return entries_tags

    def get_vocab_source(self):
        return self.vocab_source


class VocabContextEntry(
    TimestampModel, SerializeModel, VocabSourceContentModel
):
    vocab_entry = models.ForeignKey(
        VocabEntry,
        on_delete=models.CASCADE
    )
    vocab_context = models.ForeignKey(
        VocabContext,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("vocab_entry", "vocab_context")
        verbose_name = _("label_vocab_entry_context")
        verbose_name_plural = _("label_vocab_entry_context_plural")

    def __str__(self):
        return "vocab_entry: {0}, vocab_context: {1}".format(
            self.vocab_entry_id,
            self.vocab_context_id
        )

    def get_serializer(self):
        from .serializers import VocabContextEntrySerializer
        return VocabContextEntrySerializer

    def get_vocab_entry_tags(self):
        """
        Returns a list of the content of the object's VocabEntryTags.
        """
        tags = []
        for tag in self.vocab_entry_tags.all():
            tags.append(tag.content)
        tags.sort()
        return tags

    def get_tagged_context(self):
        tags = self.get_vocab_entry_tags()
        tagged_text = tag_text(tags, self.vocab_context.content)
        return tagged_text

    def add_vocab_entry_tag(self, tag):
        VocabEntryTag.objects.create(
            vocab_context_entry=self,
            content=tag
        )

    def remove_vocab_entry_tag(self, tag):
        VocabEntryTag.objects.filter(
            vocab_context_entry=self,
            content=tag
        ).delete()

    def get_vocab_source(self):
        return self.vocab_context.vocab_source


class VocabEntryTag(VocabSourceContentModel):
    vocab_context_entry = models.ForeignKey(
        VocabContextEntry,
        related_name="vocab_entry_tags",
        on_delete=models.CASCADE
    )
    content = models.TextField(
        verbose_name=_("label_content"),
    )

    def get_vocab_source(self):
        return self.vocab_context_entry.vocab_context.vocab_source
