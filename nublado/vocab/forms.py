from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from core.forms import BaseModelForm
from .models import (
    VocabEntry, VocabContext, VocabSource
)

User = get_user_model()


class VocabEntryForm(BaseModelForm):

    class Meta:
        abstract = True
        fields = [
            'language', 'entry', 'pronunciation_spelling',
            'pronunciation_ipa', 'description'
        ]
        error_messages = {
            'entry': {
                'required': _('validation_field_required'),
                'unique': _('validation_field_unique'),
            }
        }


class VocabContextForm(BaseModelForm):

    class Meta:
        abstract = True
        fields = ['content']
        error_messages = {
            'content': {
                'required': _('validation_field_required'),
            }
        }


class VocabSourceForm(BaseModelForm):

    class Meta:
        abstract = True
        fields = ['name', 'description', 'source_type']
        error_messages = {
            'name': {
                'required': _('validation_field_required'),
                'unique': _('validation_field_unique'),
            }
        }


class VocabEntrySearchForm(forms.Form):
    pass


class VocabEntryCreateForm(VocabEntryForm):

    class Meta(VocabEntryForm.Meta):
        model = VocabEntry

    def clean(self):
        cleaned_data = super().clean()
        if all(k in cleaned_data for k in ('entry', 'language')):
            if VocabEntry.objects.filter(
                entry=cleaned_data['entry'],
                language=cleaned_data['language']
            ).exists():
                self.add_error('entry', _('validation_vocab_entry_unique'))


class VocabEntryUpdateForm(VocabEntryForm):

    class Meta(VocabEntryForm.Meta):
        model = VocabEntry


class VocabContextCreateForm(VocabContextForm):

    class Meta(VocabContextForm.Meta):
        model = VocabContext

    def __init__(self, *args, **kwargs):
        self.vocab_source = kwargs.pop('vocab_source', None)
        self.creator = kwargs.pop('creator', None)
        super(VocabContextCreateForm, self).__init__(*args, **kwargs)
        if not self.vocab_source:
            raise ValueError(_('validation_vocab_source_required'))
        self.instance.vocab_source = self.vocab_source


class VocabContextUpdateForm(VocabContextForm):

    class Meta(VocabContextForm.Meta):
        model = VocabContext


class VocabSourceCreateForm(VocabSourceForm):

    def __init__(self, *args, **kwargs):
        self.vocab_project = kwargs.pop('vocab_project', None)
        self.creator = kwargs.pop('creator', None)
        super(VocabSourceCreateForm, self).__init__(*args, **kwargs)
        if not self.vocab_project:
            raise ValueError(_('validation_vocab_project_required'))
        if not self.creator:
            raise ValueError(_('validation_vocab_content_creator_required'))
        self.instance.vocab_project = self.vocab_project
        self.instance.creator = self.creator

    class Meta(VocabSourceForm.Meta):
        model = VocabSource


class VocabSourceUpdateForm(VocabSourceForm):

    class Meta(VocabSourceForm.Meta):
        model = VocabSource
