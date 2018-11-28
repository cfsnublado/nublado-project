from django.urls import path, re_path
from django.conf.urls import include
from rest_framework.authtoken import views
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework.routers import DefaultRouter
from users.api.views_api import UserViewSet, ProfileViewSet
from vocab.api.views_api import (
    NestedVocabContextEntryViewSet, NestedVocabContextViewSet, VocabEntryViewSet,
    NestedVocabSourceViewSet, VocabContextEntryViewSet, VocabContextViewSet,
    VocabEntryExportView, VocabEntryLanguageExportView, VocabEntryImportView,
    VocabProjectViewSet, VocabSourceImportView, VocabSourceExportView,
    VocabSourceViewSet
)
app_name = 'app'

router = DefaultRouter()

# users
router.register(r'user', UserViewSet, base_name='user')
router.register(r'profile', ProfileViewSet, base_name='profile')
# vocab
router.register(r'entry', VocabEntryViewSet, base_name='vocab-entry')
router.register(r'project', VocabProjectViewSet, base_name='vocab-project')
router.register(r'source', VocabSourceViewSet, base_name='vocab-source')
router.register(r'vocab-context', VocabContextViewSet, base_name='vocab-context')
router.register(r'vocab-context-entry', VocabContextEntryViewSet, base_name='vocab-context-entry')
vocab_source_router = NestedSimpleRouter(router, r'project', lookup='vocab_project')
vocab_source_router.register(r'vocab-source', NestedVocabSourceViewSet, base_name='nested-vocab-source')
vocab_context_router = NestedSimpleRouter(router, r'source', lookup='vocab_source')
vocab_context_router.register(r'vocab-context', NestedVocabContextViewSet, base_name='nested-vocab-context')
vocab_entry_context_router = NestedSimpleRouter(router, r'vocab-context', lookup='vocab_context')
vocab_entry_context_router.register(
    r'vocab-context-entry',
    NestedVocabContextEntryViewSet,
    base_name='nested-vocab-context-entry'
)
urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
    path('vocab/source/import/', VocabSourceImportView.as_view(), name='vocab_source_import'),
    re_path(
        '^vocab/source/(?P<vocab_source_pk>[\d]+)/export/$',
        VocabSourceExportView.as_view(),
        name='vocab_source_export'
    ),
    path('vocab/entries/import/', VocabEntryImportView.as_view(), name='vocab_entries_import'),
    path('vocab/entries/export/', VocabEntryExportView.as_view(), name='vocab_entries_export'),
    re_path(
        '^vocab/entries/export/language/(?P<language>[a-z]{2})/$',
        VocabEntryLanguageExportView.as_view(),
        name='vocab_entries_language_export'
    ),
    path('', include(router.urls)),
    path('', include(vocab_source_router.urls)),
    path('', include(vocab_context_router.urls)),
    path('', include(vocab_entry_context_router.urls)),
]
