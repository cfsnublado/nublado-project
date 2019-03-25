import requests

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, GenericViewSet
)

from django.db.models import F, IntegerField, Value
from django.db.models.functions import Lower

from core.api.views_api import APIDefaultsMixin, StandardPagination
from ..models import (
    VocabDefinition, VocabEntry, VocabContextEntry,
    VocabContext, VocabProject, VocabSource
)
from ..serializers import (
    VocabDefinitionSerializer, VocabEntrySerializer, VocabContextEntrySerializer,
    VocabContextSerializer, VocabProjectSerializer, VocabSourceSerializer,
    VocabSourceEntrySerializer
)
from ..utils import (
    export_vocab_entries, export_vocab_source,
    import_vocab_entries, import_vocab_source
)
from .permissions import CreatorPermission, ReadWritePermission, IsSuperuser
from ..conf import settings


def add_definitions_from_oxford(json_data, vocab_entry):
    '''
    json_data: The json returned from the Oxford api for a vocab entry.
    '''

    lexical_categories = {
        'noun': VocabDefinition.NOUN,
        'adjective': VocabDefinition.ADJECTIVE,
        'adverb': VocabDefinition.ADVERB,
        'verb': VocabDefinition.VERB,
        'expression': VocabDefinition.EXPRESSION,
        'other': VocabDefinition.OTHER
    }

    for result in json_data['results']:
        for lexical_entry in result['lexicalEntries']:
            lexical_category = lexical_entry['lexicalCategory'].lower()

            if 'derivativeOf' not in lexical_entry:

                for entry in lexical_entry['entries']:
                    if 'senses' in entry:
                        for sense in entry['senses']:
                            if 'definitions' in sense:
                                for definition in sense['definitions']:
                                    if lexical_category not in lexical_categories:
                                        lexical_category = 'other'
                                    VocabDefinition.objects.create(
                                        vocab_entry=vocab_entry,
                                        definition_type=lexical_categories[lexical_category],
                                        definition=definition
                                    )


class SmallPagination(StandardPagination):
    page_size = 10


class LargePagination(StandardPagination):
    page_size = 100


class BatchMixin(object):

    @action(methods=['post'], detail=False)
    def create_batch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VocabProjectViewSet(APIDefaultsMixin, ModelViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabProjectSerializer
    queryset = VocabProject.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class VocabEntryViewSet(APIDefaultsMixin, BatchMixin, ModelViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabEntrySerializer
    permission_classes = [ReadWritePermission]
    pagination_class = LargePagination

    def get_queryset(self):
        language = self.request.query_params.get('language', None)
        qs = VocabEntry.objects.order_by('entry')

        if language:
            qs = qs.filter(language=language)

        return qs

    @action(methods=['get'], detail=False)
    def detail_data(self, request):
        '''
        Retrieve VocabEntry object
        '''
        entry = request.query_params.get('entry', None)
        language = request.query_params.get('language', 'en')

        if not entry:
            raise ParseError('Vocab entry required.')

        vocab_entry = get_object_or_404(
            VocabEntry,
            language=language,
            entry=entry
        )
        serializer = self.get_serializer(vocab_entry)

        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )


class VocabEntryImportView(APIDefaultsMixin, APIView):
    permission_classes = [
        IsAuthenticated, IsSuperuser
    ]

    def post(self, request, *args, **kwargs):
        data = request.data

        if 'vocab_entries' in data:
            import_vocab_entries(data)
            return Response(data={'success_msg': 'OK!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'error': 'vocab-data required'}, status=status.HTTP_400_BAD_REQUEST)


class VocabEntryExportView(APIDefaultsMixin, APIView):
    permission_classes = [
        IsAuthenticated, IsSuperuser
    ]

    def get(self, request, *args, **kwargs):
        data = export_vocab_entries(request)

        return Response(data=data)


class VocabEntryLanguageExportView(VocabEntryExportView):

    def get(self, request, *args, **kwargs):
        data = export_vocab_entries(
            request,
            language=kwargs['language']
        )

        return Response(data=data)


class VocabDefinitionViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabDefinitionSerializer
    queryset = VocabDefinition.objects.select_related('vocab_entry')

    def get_permissions(self):
        # list, create, retrieve, update, partial_update, destroy
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = []

        return super(APIDefaultsMixin, self).get_permissions()


class NestedVocabDefinitionViewSet(
    APIDefaultsMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    OXFORD_API_ID = getattr(settings, 'OXFORD_API_ID', None)
    OXFORD_API_KEY = getattr(settings, 'OXFORD_API_KEY', None)

    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabDefinition.objects.select_related('vocab_entry')
    serializer_class = VocabDefinitionSerializer
    vocab_entry = None
    oxford_entry_url = 'https://od-api.oxforddictionaries.com/api/v1/entries/{0}/{1}'
    oxford_headers = {
        'Accept': 'application/json',
        'app_id': OXFORD_API_ID,
        'app_key': OXFORD_API_KEY
    }

    def get_vocab_entry(self, vocab_entry_pk=None):
        if not self.vocab_entry:
            self.vocab_entry = get_object_or_404(VocabEntry, id=vocab_entry_pk)

        return self.vocab_entry

    def perform_create(self, serializer):
        vocab_entry = self.get_vocab_entry(
            vocab_entry_pk=self.kwargs['vocab_entry_pk']
        )
        serializer.save(
            creator=self.request.user,
            vocab_entry=vocab_entry
        )

    def get_queryset(self):
        return self.queryset.filter(vocab_entry_id=self.kwargs['vocab_entry_pk'])

    def get_permissions(self):
        # list, create, retrieve, update, partial_update, destroy
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = []

        return super(APIDefaultsMixin, self).get_permissions()

    def list(self, request, *args, **kwargs):
        self.get_vocab_entry(vocab_entry_pk=kwargs['vocab_entry_pk'])

        # If no definitions in db, check the oxford api.
        if not VocabDefinition.objects.filter(vocab_entry=self.vocab_entry).exists():
            url = self.oxford_entry_url.format(
                self.vocab_entry.language,
                self.vocab_entry.entry
            )
            response = requests.get(url, headers=self.oxford_headers)

            if response.status_code == status.HTTP_200_OK:
                response_json = response.json()
                add_definitions_from_oxford(response_json, self.vocab_entry)

        return super(NestedVocabDefinitionViewSet, self).list(request, *args, **kwargs)


class VocabSourceViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabSourceSerializer
    queryset = VocabSource.objects.prefetch_related('vocab_contexts')


class NestedVocabSourceViewSet(
    APIDefaultsMixin, BatchMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabSource.objects.select_related('vocab_project')
    serializer_class = VocabSourceSerializer
    vocab_project = None

    def get_vocab_project(self, vocab_project_pk=None):
        if not self.vocab_project:
            self.vocab_project = get_object_or_404(VocabProject, id=vocab_project_pk)

        return self.vocab_project

    def create(self, request, *args, **kwargs):
        vocab_project = self.get_vocab_project(vocab_project_pk=kwargs['vocab_project_pk'])
        self.check_object_permissions(request, vocab_project)

        return super(NestedVocabSourceViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        vocab_project = self.get_vocab_project(vocab_project_pk=self.kwargs['vocab_project_pk'])
        serializer.save(
            creator=self.request.user,
            vocab_project=vocab_project
        )

    def get_queryset(self):
        return self.queryset.filter(vocab_project_id=self.kwargs['vocab_project_pk'])

    def list(self, request, *args, **kwargs):
        self.get_vocab_project(vocab_project_pk=kwargs['vocab_project_pk'])

        return super(NestedVocabSourceViewSet, self).list(request, *args, **kwargs)


class VocabSourceEntryViewSet(APIDefaultsMixin, ListModelMixin, GenericViewSet):
    vocab_source_pk = None
    permission_classes = [ReadWritePermission]
    pagination_class = LargePagination

    def get_queryset(self):
        language = self.request.query_params.get('language', None)
        qs = VocabContextEntry.objects.select_related('vocab_context', 'vocab_entry')

        if language:
            qs = qs.filter(vocab_entry__language=language)

        qs = qs.filter(vocab_context__vocab_source_id=self.vocab_source_pk)
        qs = qs.order_by('vocab_entry__entry').distinct()
        qs = qs.values(
            language=Lower('vocab_entry__language'),
            slug=Lower('vocab_entry__slug'),
            entry=Lower('vocab_entry__entry')
        )
        qs = qs.annotate(vocab_source_id=Value(self.vocab_source_pk, output_field=IntegerField()))
        qs = qs.annotate(id=F('vocab_entry_id'))

        return qs

    def list(self, request, vocab_source_pk=None):

        if not vocab_source_pk:
            raise ParseError('Vocab source required.')
        else:
            self.vocab_source_pk = vocab_source_pk

        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = VocabSourceEntrySerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            serializer = VocabSourceEntrySerializer(
                qs,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)


class VocabSourceImportView(APIDefaultsMixin, APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        import_vocab_source(data, request.user)

        return Response(data={'success_msg': 'OK!'}, status=status.HTTP_201_CREATED)


class VocabSourceExportView(APIDefaultsMixin, APIView):
    permission_classes = [
        IsAuthenticated, CreatorPermission
    ]

    def get(self, request, *args, **kwargs):
        vocab_source = self.get_object()
        data = export_vocab_source(request, vocab_source)

        return Response(data=data)

    def get_object(self):
        obj = get_object_or_404(
            VocabSource.objects.prefetch_related(
                'creator',
                'vocab_contexts__vocabcontextentry_set__vocab_entry'
            ),
            id=self.kwargs['vocab_source_pk']
        )
        self.check_object_permissions(self.request, obj)

        return obj


class VocabContextViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabContextSerializer
    queryset = VocabContext.objects.select_related('vocab_source')

    @action(methods=['post'], detail=True)
    def add_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        if not VocabContextEntry.objects.filter(vocab_entry_id=vocab_entry_id, vocab_context_id=pk).exists():
            VocabContextEntry.objects.create(vocab_entry_id=vocab_entry_id, vocab_context_id=pk)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True)
    def add_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        vocab_entry_tag = request.data.get('vocab_entry_tag', None)

        if not vocab_entry_tag:
            raise ParseError('vocab_entry_tag required')

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.add_vocab_entry_tag(vocab_entry_tag)

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['delete', 'post'], detail=True)
    def remove_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete', 'post'], detail=True)
    def remove_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        vocab_entry_tag = request.data.get('vocab_entry_tag', None)

        if not vocab_entry_tag:
            raise ParseError('vocab_entry_tag required')

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.remove_vocab_entry_tag(vocab_entry_tag)

        return Response(status=status.HTTP_204_NO_CONTENT)


class NestedVocabContextViewSet(
    APIDefaultsMixin, BatchMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContext.objects.select_related('vocab_source')
    serializer_class = VocabContextSerializer
    vocab_source = None

    def get_vocab_source(self, vocab_source_pk=None):
        if not self.vocab_source:
            self.vocab_source = get_object_or_404(VocabSource, id=vocab_source_pk)

        return self.vocab_source

    def create(self, request, *args, **kwargs):
        vocab_source = self.get_vocab_source(vocab_source_pk=kwargs['vocab_source_pk'])
        self.check_object_permissions(request, vocab_source)

        return super(NestedVocabContextViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        vocab_source = self.get_vocab_source(vocab_source_pk=self.kwargs['vocab_source_pk'])
        serializer.save(vocab_source=vocab_source)

    def get_queryset(self):
        return self.queryset.filter(vocab_source_id=self.kwargs['vocab_source_pk'])

    def list(self, request, *args, **kwargs):
        self.get_vocab_source(vocab_source_pk=kwargs['vocab_source_pk'])

        return super(NestedVocabContextViewSet, self).list(request, *args, **kwargs)


class VocabContextEntryViewSet(
    APIDefaultsMixin, RetrieveModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContextEntry.objects.select_related(
        'vocab_entry', 'vocab_context', 'vocab_context__vocab_source'
    ).prefetch_related(
        'vocab_entry_tags'
    )
    serializer_class = VocabContextEntrySerializer
    permission_classes = [ReadWritePermission]
    pagination_class = SmallPagination

    def get_queryset(self):
        vocab_entry_id = self.request.query_params.get('vocab_entry', None)
        if vocab_entry_id:
            return self.queryset.filter(vocab_entry_id=vocab_entry_id)
        else:
            return self.queryset

    @action(methods=['get'], detail=False)
    def detail_data(self, request):
        '''
        Retrieve VocabEntry object based on entry post data.
        '''
        vocab_entry_id = request.query_params.get('vocab_entry', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry required')

        vocab_context_id = request.query_params.get('vocab_context', None)

        if not vocab_context_id:
            raise ParseError('vocab_context_id required')

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_context_id=vocab_context_id,
            vocab_entry_id=vocab_entry_id
        )
        serializer = self.get_serializer(vocab_entry_context)

        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )


class NestedVocabContextEntryViewSet(APIDefaultsMixin, CreateModelMixin, ListModelMixin, GenericViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContextEntry.objects.select_related(
        'vocab_entry', 'vocab_context', 'vocab_context__vocab_source'
    ).prefetch_related(
        'vocab_entry_tags'
    )
    serializer_class = VocabContextEntrySerializer
    vocab_entry = None
    vocab_context = None

    def get_vocab_entry(self, vocab_entry_entry=None):
        if not self.vocab_entry:
            self.vocab_entry = get_object_or_404(VocabEntry, entry=vocab_entry_entry)

        return self.vocab_entry

    def get_vocab_context(self, vocab_context_pk=None):
        if not self.vocab_context:
            self.vocab_context = get_object_or_404(VocabContext, pk=vocab_context_pk)

        return self.vocab_context

    def get_queryset(self):
        return self.queryset.filter(vocab_context_id=self.kwargs['vocab_context_pk'])

    def perform_create(self, serializer):
        # Vocab entry text from request
        vocab_entry_entry = self.request.data.get('vocab_entry_entry', None)

        if not vocab_entry_entry:
            raise ParseError('vocab_entry_entry required')

        vocab_entry = self.get_vocab_entry(vocab_entry_entry=vocab_entry_entry)
        vocab_context = self.get_vocab_context(vocab_context_pk=self.kwargs['vocab_context_pk'])
        serializer.save(vocab_entry=vocab_entry, vocab_context=vocab_context)

    def list(self, request, *args, **kwargs):
        self.get_vocab_context(vocab_context_pk=kwargs['vocab_context_pk'])

        return super(NestedVocabContextEntryViewSet, self).list(request, *args, **kwargs)
