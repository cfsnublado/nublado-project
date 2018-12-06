
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from core.api.views_api import APIDefaultsMixin
from ..models import (
    VocabEntry, VocabContextEntry, VocabContext,
    VocabProject, VocabSource
)
from ..serializers import (
    VocabEntrySerializer, VocabContextEntrySerializer, VocabContextSerializer,
    VocabProjectSerializer, VocabSourceSerializer
)
from ..utils import (
    export_vocab_entries, export_vocab_source,
    import_vocab_entries, import_vocab_source
)
from .permissions import CreatorPermission, IsSuperuser


class BatchMixin(object):

    @action(methods=['post'], detail=False)
    def create_batch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VocabProjectViewSet(APIDefaultsMixin, ModelViewSet):
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    serializer_class = VocabProjectSerializer
    queryset = VocabProject.objects.all()
    permission_classes = (
        IsAuthenticated,
    )


class VocabEntryViewSet(APIDefaultsMixin, BatchMixin, ModelViewSet):
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    serializer_class = VocabEntrySerializer
    queryset = VocabEntry.objects.all()
    permission_classes = (
        IsAuthenticated,
    )

    @action(methods=['get'], detail=False)
    def detail_data(self, request):
        '''
        Retrieve VocabEntry object
        '''
        entry = request.query_params.get('entry', None)
        language = request.query_params.get('language', None)
        if not entry or not language:
            raise ParseError('Vocab entry and language required.')
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
    permission_classes = (
        IsAuthenticated,
        IsSuperuser
    )

    def post(self, request, *args, **kwargs):
        data = request.data
        if 'vocab_entries' in data:
            import_vocab_entries(data)
            return Response(data={'success_msg': 'OK!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'error': 'vocab-data required'}, status=status.HTTP_400_BAD_REQUEST)


class VocabEntryExportView(APIDefaultsMixin, APIView):
    permission_classes = (
        IsAuthenticated,
        IsSuperuser
    )

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


class VocabSourceViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabSourceSerializer
    queryset = VocabSource.objects.prefetch_related('vocab_contexts')
    permission_classes = (
        IsAuthenticated,
    )


class NestedVocabSourceViewSet(
    APIDefaultsMixin, BatchMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabSource.objects.select_related('vocab_project')
    serializer_class = VocabSourceSerializer
    permission_classes = (
        IsAuthenticated,
    )
    vocab_project = None

    def get_vocab_project(self, vocab_project_slug=None):
        if not self.vocab_project:
            self.vocab_project = get_object_or_404(VocabProject, slug=vocab_project_slug)
        return self.vocab_project

    def create(self, request, *args, **kwargs):
        vocab_project = self.get_vocab_project(vocab_project_slug=kwargs['vocab_project_slug'])
        self.check_object_permissions(request, vocab_project)
        return super(NestedVocabSourceViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        vocab_project = self.get_vocab_project(vocab_project_slug=self.kwargs['vocab_project_slug'])
        serializer.save(vocab_source=vocab_project)

    def get_queryset(self):
        return self.queryset.filter(vocab_project__slug=self.kwargs['vocab_project_slug'])

    def list(self, request, *args, **kwargs):
        self.get_vocab_project(vocab_project_slug=kwargs['vocab_project_slug'])
        return super(NestedVocabSourceViewSet, self).list(request, *args, **kwargs)


class VocabSourceImportView(APIDefaultsMixin, APIView):
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request, *args, **kwargs):
        data = request.data
        import_vocab_source(data, request.user)
        return Response(data={'success_msg': 'OK!'}, status=status.HTTP_201_CREATED)


class VocabSourceExportView(APIDefaultsMixin, APIView):
    permission_classes = (
        IsAuthenticated,
        CreatorPermission
    )

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
    permission_classes = (
        IsAuthenticated,
    )

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
    permission_classes = (
        IsAuthenticated,
    )
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
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContextEntry.objects.select_related('vocab_entry', 'vocab_context').prefetch_related('vocab_entry_tags')
    serializer_class = VocabContextEntrySerializer
    permission_classes = (
        IsAuthenticated,
    )

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
    queryset = VocabContextEntry.objects.select_related('vocab_entry', 'vocab_context')
    serializer_class = VocabContextEntrySerializer
    permission_classes = (
        IsAuthenticated,
    )
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
