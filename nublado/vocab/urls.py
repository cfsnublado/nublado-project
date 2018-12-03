from django.urls import path, re_path

from .views.views_vocab_auth import VocabUserDashboardView
from .views.views_vocab_context_auth import (
    VocabContextCreateView, VocabContextDeleteView, VocabContextTagView,
    VocabContextEntryTagView
)
from .views.views_vocab_entry import (
    VocabEntrySearchView
)
from .views.views_vocab_entry_auth import (
    VocabEntriesView, VocabEntryContextsView,
    VocabEntryCreateView, VocabEntryDeleteView, VocabEntriesExportJsonView,
    VocabEntryDashboardView,
    VocabEntryUpdateView
)
from .views.views_vocab_project_auth import (
    VocabProjectCreateView, VocabProjectDashboardView, VocabProjectDeleteView,
    VocabProjectSourcesView, VocabProjectUpdateView
)
from .views.views_vocab_source_auth import (
    VocabSourceCreateView, VocabSourceDeleteView, VocabSourceExportJsonView,
    VocabSourceContextsView, VocabSourceDashboardView,
    VocabSourceEntriesView, VocabSourceEntryContextsView,
    VocabSourceUpdateView
)
from .views.views_vocab_autocomplete import (
    VocabEntryAutocompleteView, VocabProjectSourceAutocompleteView,
    VocabSourceEntryAutocompleteView
)


app_name = 'vocab'

urlpatterns = [
    path('', VocabUserDashboardView.as_view(), name='vocab_user_dashboard'),
    re_path(
        '^autocomplete/entry/(?P<language>[a-z]{2})/$',
        VocabEntryAutocompleteView.as_view(),
        name='vocab_entry_autocomplete'
    ),
    path(
        'autocomplete/project/<int:vocab_project_pk>/source/',
        VocabProjectSourceAutocompleteView.as_view(),
        name='vocab_project_source_autocomplete'
    ),
    path(
        'autocomplete/source/<int:vocab_source_pk>/entry/',
        VocabSourceEntryAutocompleteView.as_view(),
        name='vocab_source_entry_autocomplete'
    ),
    re_path(
        '^autocomplete/source/(?P<vocab_source_pk>[-?\d]+)/entry/(?P<language>[a-z]{2})/$',
        VocabSourceEntryAutocompleteView.as_view(),
        name='vocab_source_entry_language_autocomplete'
    ),
    path(
        'search',
        VocabEntrySearchView.as_view(),
        name='vocab_entry_search'
    ),
    path(
        'project/create/',
        VocabProjectCreateView.as_view(),
        name='vocab_project_create'
    ),
    path(
        'project/<int:vocab_project_pk>-<slug:vocab_project_slug>/update/',
        VocabProjectUpdateView.as_view(),
        name='vocab_project_update'
    ),
    path('project/<int:vocab_project_pk>/delete/', VocabProjectDeleteView.as_view(), name='vocab_project_delete'),
    path(
        'project/<int:vocab_project_pk>-<slug:vocab_project_slug>/dashboard/',
        VocabProjectDashboardView.as_view(),
        name='vocab_project_dashboard'
    ),
    path(
        'project/<int:vocab_project_pk>-<slug:vocab_project_slug>/sources/',
        VocabProjectSourcesView.as_view(),
        name='vocab_project_sources'
    ),
    path(
        'project/<int:vocab_project_pk>-<slug:vocab_project_slug>/source/create/',
        VocabSourceCreateView.as_view(),
        name='vocab_source_create'
    ),
    path('entries/export/', VocabEntriesExportJsonView.as_view(), name='vocab_entries_export_json'),
    path('entries/', VocabEntriesView.as_view(), name='vocab_entries'),
    re_path(
        '^entry/(?P<vocab_entry_language>[a-z]{2})/(?P<vocab_entry_slug>[-\w]+)/$',
        VocabEntryDashboardView.as_view(),
        name='vocab_entry_dashboard'
    ),
    re_path(
        '^entry/(?P<vocab_entry_language>[a-z]{2})/(?P<vocab_entry_slug>[-\w]+)/contexts/$',
        VocabEntryContextsView.as_view(),
        name='vocab_entry_contexts'
    ),
    path('entry/create/', VocabEntryCreateView.as_view(), name='vocab_entry_create'),
    re_path(
        '^entry/(?P<vocab_entry_language>[a-z]{2})/(?P<vocab_entry_slug>[-\w]+)/update/$',
        VocabEntryUpdateView.as_view(),
        name='vocab_entry_update'
    ),
    path('entry/<int:vocab_entry_pk>/delete/', VocabEntryDeleteView.as_view(), name='vocab_entry_delete'),
    path(
        'source/<int:vocab_source_pk>-<slug:vocab_source_slug>/dashboard/',
        VocabSourceDashboardView.as_view(),
        name='vocab_source_dashboard'
    ),
    path(
        'source/<int:vocab_source_pk>-<slug:vocab_source_slug>/update/',
        VocabSourceUpdateView.as_view(),
        name='vocab_source_update'
    ),
    path('source/<int:vocab_source_pk>/delete/', VocabSourceDeleteView.as_view(), name='vocab_source_delete'),
    path(
        'source/<int:vocab_source_pk>)/export/',
        VocabSourceExportJsonView.as_view(),
        name='vocab_source_export_json'
    ),
    path(
        'source/<int:vocab_source_pk>-<slug:vocab_source_slug>/entries/',
        VocabSourceEntriesView.as_view(),
        name='vocab_source_entries'
    ),
    path(
        'source/<int:vocab_source_pk>-<slug:vocab_source_slug>/contexts/',
        VocabSourceContextsView.as_view(),
        name='vocab_source_contexts'
    ),
    re_path(
        '^source/(?P<vocab_source_pk>[\d]+)-(?P<vocab_source_slug>[-\w]+)'
        '/entry/(?P<vocab_entry_language>[a-z]{2})/(?P<vocab_entry_slug>[-\w]+)/contexts/$',
        VocabSourceEntryContextsView.as_view(),
        name='vocab_source_entry_contexts'
    ),
    path(
        'source/<int:vocab_source_pk>-<slug:vocab_source_slug>/context/create',
        VocabContextCreateView.as_view(),
        name='vocab_context_create'
    ),
    path('context/<int:vocab_context_pk>/edit/', VocabContextTagView.as_view(), name='vocab_context_tag'),
    path('context/<int:vocab_context_pk>/delete/', VocabContextDeleteView.as_view(), name='vocab_context_delete'),
    path(
        'vocabcontextentry/<int:vocab_context_entry_pk>/tag/',
        VocabContextEntryTagView.as_view(),
        name='vocab_context_entry_tag'
    ),
]
