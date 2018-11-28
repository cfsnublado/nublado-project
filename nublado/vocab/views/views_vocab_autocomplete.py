from django.views.generic import View

from core.views import AutocompleteMixin
from ..models import VocabContextEntry, VocabEntry, VocabSource


class VocabSourceAutocompleteView(AutocompleteMixin, View):
    search_model = VocabSource
    search_field = 'name'
    search_filter = 'istartswith'
    id_attr = 'id'
    label_attr = 'name'
    value_attr = 'name'


class VocabProjectSourceAutocompleteView(VocabSourceAutocompleteView):
    '''
    Autocomplete for sources in a project.
    '''

    def get_queryset(self, **kwargs):
        qs = super(VocabProjectSourceAutocompleteView, self).get_queryset(**kwargs)
        qs = qs.filter(vocab_project_id=self.kwargs['vocab_project_pk'])
        return qs


class VocabSourceCreatorAutocompleteView(VocabSourceAutocompleteView):
    '''
    Autocomplete for sources belonging to authernticated user.
    '''

    def get_queryset(self, **kwargs):
        qs = super(VocabSourceCreatorAutocompleteView, self).get_queryset(**kwargs)
        qs = qs.filter(creator_id=self.request.user.id)
        return qs


class VocabSourceEntryAutocompleteView(AutocompleteMixin, View):
    search_model = VocabContextEntry
    search_field = 'vocab_entry__entry'
    id_attr = 'vocab_entry_id'
    language_attr = 'vocab_entry__language'
    extra_attr = {'language': language_attr}

    def get_queryset(self, **kwargs):
        qs = super(VocabSourceEntryAutocompleteView, self).get_queryset(**kwargs)
        qs = qs.select_related('vocab_context', 'vocab_entry')
        qs = qs.filter(vocab_context__vocab_source_id=self.kwargs['vocab_source_pk'])
        language = self.kwargs.get('language', None)
        if language:
            qs = qs.filter(vocab_entry__language=self.kwargs['language'])
        qs = qs.values(self.id_attr, self.search_field, self.language_attr)
        qs = qs.distinct(self.search_field, self.id_attr)
        return qs

    def set_id_attr(self, obj):
        return obj[self.id_attr]

    def set_label_attr(self, obj):
        return '{0} - {1}'.format(obj['vocab_entry__language'], obj['vocab_entry__entry'])

    def set_value_attr(self, obj):
        return obj['vocab_entry__entry']

    def set_extra_attr(self, obj):
        extra_dict = {}
        for key, value in self.extra_attr.items():
            extra_dict[key] = obj[value]
        return extra_dict


class VocabEntryAutocompleteView(AutocompleteMixin, View):
    search_model = VocabEntry
    search_field = 'entry'
    id_attr = 'id'
    value_attr = 'entry'
    extra_attr = {'language': 'language'}

    def get_queryset(self, **kwargs):
        qs = super(VocabEntryAutocompleteView, self).get_queryset(**kwargs)
        language = self.kwargs.get('language', None)
        if language:
            qs = qs.filter(language=language)
        return qs

    def set_label_attr(self, obj):
        return '{0} - {1}'.format(obj.language, obj.entry)
