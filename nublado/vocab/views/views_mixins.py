from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from core.views import CachedObjectMixin, ObjectSessionMixin
from ..conf import settings
from ..models import VocabEntry, VocabProject, VocabSource


class VocabSessionMixin(ObjectSessionMixin):

    def setupSession(self, request, *args, **kwargs):
        if 'vocab_entry' in request.session:
            del request.session['vocab_entry']
        if 'vocab_source' in request.session:
            del request.session['vocab_source']
        if 'vocab_project' in request.session:
            del request.session['vocab_project']


class PermissionMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.check_permission()
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)

    def check_permission(self, *args, **kwargs):
        raise NotImplementedError('Method check_permission needs to be implemented.')


class VocabProjectSessionMixin(ObjectSessionMixin):
    session_obj = 'vocab_project'
    session_obj_attrs = ['id', 'name', 'slug']

    def setupSession(self, request, *args, **kwargs):
        super(VocabProjectSessionMixin, self).setupSession(request, *args, **kwargs)
        if 'vocab_entry' in request.session:
            del request.session['vocab_entry']
        if 'vocab_source' in request.session:
            del request.session['vocab_source']


class VocabProjectMixin(
    CachedObjectMixin, VocabProjectSessionMixin,
):
    vocab_project_id = 'vocab_project_pk'
    vocab_project_slug = 'vocab_project_slug'
    vocab_project = None

    def dispatch(self, request, *args, **kwargs):
        self.get_vocab_project(request, *args, **kwargs)
        return super(VocabProjectMixin, self).dispatch(request, *args, **kwargs)

    def get_vocab_project(self, request, *args, **kwargs):
        if self.vocab_project_id in kwargs:
            self.vocab_project = get_object_or_404(
                VocabProject.objects.prefetch_related('owner'),
                id=kwargs[self.vocab_project_id]
            )
        elif self.vocab_project_slug in kwargs:
            self.vocab_project = get_object_or_404(
                VocabProject.objects.prefetch_related('owner'),
                slug=kwargs[self.vocab_project_slug]
            )
        else:
            obj = self.get_object()
            if hasattr(obj, 'vocab_project_id'):
                self.vocab_project = obj.vocab_project
            elif isinstance(obj, VocabProject):
                self.vocab_project = obj
            else:
                raise Http404('Vocab project not found.')

    def get_context_data(self, **kwargs):
        context = super(VocabProjectMixin, self).get_context_data(**kwargs)
        context['vocab_project'] = self.vocab_project
        return context


class VocabSourcePermissionMixin(PermissionMixin):
    is_vocab_source_creator = False

    def get_context_data(self, **kwargs):
        context = super(VocabSourcePermissionMixin, self).get_context_data(**kwargs)
        context['is_vocab_source_creator'] = self.is_vocab_source_creator
        return context

    def check_permission(self):
        if self.vocab_source.creator_id == self.request.user.id:
            self.is_vocab_source_creator = True
        else:
            raise PermissionDenied


class VocabSourceSessionMixin(ObjectSessionMixin):
    session_obj = 'vocab_source'
    session_obj_attrs = ['id', 'name', 'slug']

    def setupSession(self, request, *args, **kwargs):
        super(VocabSourceSessionMixin, self).setupSession(request, *args, **kwargs)
        if 'vocab_entry' in request.session:
            del request.session['vocab_entry']
        if 'vocab_project' in request.session:
            del request.session['vocab_project']


class VocabSourceMixin(
    CachedObjectMixin, VocabSourceSessionMixin,
    VocabSourcePermissionMixin
):
    vocab_source_id = 'vocab_source_pk'
    vocab_source_slug = 'vocab_source_slug'
    vocab_project = None
    vocab_source = None

    def dispatch(self, request, *args, **kwargs):
        self.get_vocab_source(request, *args, **kwargs)
        return super(VocabSourceMixin, self).dispatch(request, *args, **kwargs)

    def get_vocab_source(self, request, *args, **kwargs):
        if self.vocab_source_id in kwargs:
            self.vocab_source = get_object_or_404(
                VocabSource.objects.prefetch_related('creator', 'vocab_project'),
                id=kwargs[self.vocab_source_id]
            )
        elif self.vocab_source_slug in kwargs:
            self.vocab_source = get_object_or_404(
                VocabSource.objects.prefetch_related('creator', 'vocab_project'),
                slug=kwargs[self.vocab_source_slug]
            )
        else:
            obj = self.get_object()
            if hasattr(obj, 'vocab_source_id'):
                self.vocab_source = obj.vocab_source
            elif isinstance(obj, VocabSource):
                    self.vocab_source = obj
            else:
                raise Http404('Vocab source not found.')
        self.vocab_project = self.vocab_source.vocab_project

    def get_context_data(self, **kwargs):
        context = super(VocabSourceMixin, self).get_context_data(**kwargs)
        context['vocab_project'] = self.vocab_project
        context['vocab_source'] = self.vocab_source
        return context


class VocabSourceSearchMixin(object):
    search_term = None
    vocab_source = None

    def dispatch(self, request, *args, **kwargs):
        self.search_term = self.request.GET.get('source', None)
        if self.search_term:
            try:
                self.vocab_source = VocabSource.objects.select_related('creator').get(
                    **self.get_search_query_kwargs()
                )
                return self.search_success(**kwargs)
            except VocabSource.DoesNotExist:
                pass
        return super(VocabSourceSearchMixin, self).dispatch(request, *args, **kwargs)

    def get_search_query_kwargs(self):
        return {
            'name__iexact': self.search_term
        }

    def search_success(self, **kwargs):
        return redirect(
            'vocab:vocab_source_dashboard',
            vocab_source_pk=self.vocab_source.id,
            vocab_source_slug=self.vocab_source.slug
        )

    def get_context_data(self, **kwargs):
        context = super(VocabSourceSearchMixin, self).get_context_data(**kwargs)
        context['vocab_source'] = self.vocab_source
        context['search_term'] = self.search_term
        return context


class VocabSourceSearchAuthMixin(VocabSourceSearchMixin):

    def get_search_query_kwargs(self):
        return {
            'creator_id': self.request.user.id,
            'name__iexact': self.search_term,
        }


class VocabEntryPermissionMixin(PermissionMixin):

    def check_permission(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied


class VocabEntrySessionMixin(ObjectSessionMixin):
    session_obj = 'vocab_entry'
    session_obj_attrs = ['id', 'language', 'entry', 'slug']

    def setupSession(self, request, *args, **kwargs):
        super(VocabEntrySessionMixin, self).setupSession(request, *args, **kwargs)
        if 'vocab_source' in request.session:
            del request.session['vocab_source']
        if 'vocab_project' in request.session:
            del request.session['vocab_project']


class VocabEntryMixin(
    CachedObjectMixin, VocabEntrySessionMixin,
    VocabEntryPermissionMixin
):
    vocab_entry_id = 'vocab_entry_pk'
    vocab_entry_language = 'vocab_entry_language'
    vocab_entry_slug = 'vocab_entry_slug'

    def dispatch(self, request, *args, **kwargs):
        if self.vocab_entry_id in kwargs:
            self.vocab_entry = get_object_or_404(
                VocabEntry,
                id=kwargs[self.vocab_entry_id]
            )
        if self.vocab_entry_language in kwargs and self.vocab_entry_slug in kwargs:
            self.vocab_entry = get_object_or_404(
                VocabEntry,
                language=kwargs[self.vocab_entry_language],
                slug=kwargs[self.vocab_entry_slug]
            )
        else:
            obj = self.get_object()
            if hasattr(obj, 'vocab_entry_id'):
                self.vocab_entry = obj.vocab_entry
            else:
                self.vocab_entry = obj
        return super(VocabEntryMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VocabEntryMixin, self).get_context_data(**kwargs)
        context['vocab_entry'] = self.vocab_entry
        return context


class VocabEntrySearchMixin(object):
    search_term = None
    search_language = 'en'
    vocab_entry = None

    def dispatch(self, request, *args, **kwargs):
        self.search_term = self.request.GET.get('search_entry', None)
        self.search_language = self.request.GET.get('search_language', 'en')
        if self.search_language not in settings.LANGUAGES_DICT:
            self.search_language = 'en'
        if self.search_term and self.search_language:
            try:
                self.vocab_entry = VocabEntry.objects.get(
                    **self.get_search_query_kwargs()
                )
                return self.search_success(**kwargs)
            except VocabEntry.DoesNotExist:
                pass
        return super(VocabEntrySearchMixin, self).dispatch(request, *args, **kwargs)

    def get_search_query_kwargs(self):
        return {
            'entry__iexact': self.search_term,
            'language': self.search_language
        }

    def search_success(self, **kwargs):
        return redirect(
            'vocab:vocab_entry_dashboard',
            vocab_entry_language=self.vocab_entry.language,
            vocab_entry_slug=self.vocab_entry.slug
        )

    def get_context_data(self, **kwargs):
        context = super(VocabEntrySearchMixin, self).get_context_data(**kwargs)
        context['vocab_entry'] = self.vocab_entry
        context['search_term'] = self.search_term
        context['search_language'] = self.search_language
        return context
