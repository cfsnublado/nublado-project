import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .managers import ParentManager, TranslationManager
from .validation import validate_translation_languages


# Note on naming conventions.
# All models, abstract or otherwise, that are meant to be subclassed by other models,
# are suffixed with 'Model.'

class InviteModel(models.Model):
    ACCEPTED = 3
    DECLINED = 2
    PENDING = 1
    STATUS_CHOICES = (
        (PENDING, _('label_invite_pending')),
        (ACCEPTED, _('label_invite_status_accepted')),
        (DECLINED, _('label_invite_status_declined'))
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invites_sent',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invites_received',
        on_delete=models.CASCADE

    )
    status = models.IntegerField(
        verbose_name=_('label_status'),
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def clean(self):
        # Raise error if sender and receiver refer to the same object.
        if self.sender_id == self.receiver_id:
            raise ValidationError(
                _('validation_invite_sender_receiver_equal'),
                code='invite_sender_receiver_equal'
            )

    class Meta:
        abstract = True


class LanguageModel(models.Model):
    DEFAULT_LANGUAGE = settings.LANGUAGE_CODE
    LANGUAGE_CHOICES = settings.LANGUAGES

    language = models.CharField(
        verbose_name=_('label_language'),
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE,
    )

    class Meta:
        abstract = True


class ParentModel(models.Model):
    '''
    A self-referencing, parent/children model.
    '''
    parent = models.ForeignKey(
        'self',
        db_column='parent_id',
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_children',
        on_delete=models.CASCADE
    )

    objects = ParentManager()

    @property
    def is_parent(self):
        if self.parent_id:
            return False
        else:
            return True

    class Meta:
        abstract = True


class SerializeModel(models.Model):

    serializer = None

    def get_serializer(self):
        if self.serializer is not None:
            return self.serializer(self)
        else:
            return self.serializer

    def serialize(self):
        if self.serializer is not None:
            return self.get_serializer().data

    class Meta:
        abstract = True


class SlugifyModel(models.Model):
    '''
    Models that inherit from this class get an auto filled slug property based on the models name property.
    Correctly handles duplicate values (slugs are unique), and truncates slug if value too long.
    The following attributes can be overridden on a per model basis:
    * value_field_name - the value to slugify, default 'name'
    * slug_field_name - the field to store the slugified value in, default 'slug'
    * max_iterations - how many iterations to search for an open slug before raising IntegrityError, default 1000
    * slug_separator - the character to put in place of spaces and other non url friendly characters, default '-'
    '''

    def save(self, *args, **kwargs):

        pk_field_name = self._meta.pk.name
        value_field_name = getattr(self, 'value_field_name', 'name')
        slug_field_name = getattr(self, 'slug_field_name', 'slug')
        max_iterations = getattr(self, 'slug_max_iterations', 1000)
        slug_separator = getattr(self, 'slug_separator', '-')
        unique_slug = getattr(self, 'unique_slug', True)

        if unique_slug:
            # fields, query set, other setup variables
            slug_field = self._meta.get_field(slug_field_name)
            slug_len = slug_field.max_length
            queryset = self.__class__.objects.all()
            # if the pk of the record is set, exclude it from the slug search
            current_pk = getattr(self, pk_field_name)
            if current_pk:
                queryset = queryset.exclude(**{pk_field_name: current_pk})

            # setup the original slug, and make sure it is within the allowed length
            slug = slugify(getattr(self, value_field_name))
            if slug_len:
                slug = slug[:slug_len]
            original_slug = slug

            # iterate until a unique slug is found, or max_iterations
            counter = 2
            while queryset.filter(**{slug_field_name: slug}).count() > 0 and counter < max_iterations:
                slug = original_slug
                suffix = '{0}{1}'.format(slug_separator, counter)
                if slug_len and len(slug) + len(suffix) > slug_len:
                    slug = slug[:slug_len - len(suffix)]
                slug = '{0}{1}'.format(slug, suffix)
                counter += 1

            if counter == max_iterations:
                raise IntegrityError('Unable to locate unique slug')
        else:
            slug = slugify(getattr(self, value_field_name))
        self.slug = slug

        super(SlugifyModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    date_created = models.DateTimeField(
        verbose_name=_('label_date_created'),
        default=timezone.now,
        editable=False
    )
    date_updated = models.DateTimeField(
        verbose_name=_('label_date_updated'),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True


class TrackedFieldModel(models.Model):
    # Fields to be 'listened' to for changes.
    tracked_fields = []

    def __init__(self, *args, **kwargs):
        super(TrackedFieldModel, self).__init__(*args, **kwargs)
        self.init_tracked_fields()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(TrackedFieldModel, self).save(force_insert, force_update, *args, **kwargs)
        self.init_tracked_fields()

    def init_tracked_fields(self):
        for field in self.tracked_fields:
            if hasattr(self, field):
                setattr(self, "_original_{0}".format(field), getattr(self, field))

    def field_changed(self, field):
        if hasattr(self, field) and field in self.tracked_fields:
            value = getattr(self, field)
            orig_value = getattr(self, "_original_{0}".format(field))
            return value != orig_value

    class Meta:
        abstract = True


class TranslationModel(ParentModel, LanguageModel):

    objects = TranslationManager()

    @property
    def translations(self):
        '''
        Returns reverse relation of children with the property name of translations.
        Inheriting classes need to implement this.

        Example: return self.blog_post_children
        '''
        raise NotImplementedError

    def clean(self, *args, **kwargs):
        validate_translation_languages(
            self,
            ValidationError(
                {'language': _('validation_translation_languages_equal')},
                code='translation_languages_equal'
            )
        )

    def get_available_languages(self, include_self_language=True, exceptions=None):
        '''
        Returns tuple of languages from language choices that haven't been used by
        the object's translations.
        include_self_language: whether to include self language in available languages.
        exceptions: list of used languages to be included in available languages for whatever reason.
        '''
        if self.is_parent:
            languages = list(
                self.translations.all().values_list('language', flat=True)
            )
            if not include_self_language:
                languages.append(self.language)
            if exceptions is not None:
                [languages.remove(x) for x in exceptions if x in languages]
            available_languages = dict(self.LANGUAGE_CHOICES)
            [available_languages.pop(key) for key in languages]
            return tuple(sorted(available_languages.items()))

    def get_translation(self, language):
        translation = self.translations.filter(language=language).first()
        return translation

    class Meta:
        abstract = True


class UserstampModel(models.Model):
    '''
    A model that records which user created it and which
    user last updated it.
    '''
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name='%(app_label)s_%(class)s_created_objects',
        on_delete=models.SET_NULL
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name='%(app_label)s_%(class)s_last_updated_objects',
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    '''
    A model whose id is a generated uuid.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
