from django.db.models import F, IntegerField, Value
from django.db.models.functions import Lower

from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (
    APIView, GenericViewSet
)

from core.api.views_api import APIDefaultsMixin
from ..models import VocabContextEntry, VocabProject, VocabSource
from ..serializers import (
    VocabSourceSerializer, VocabSourceEntrySerializer
)
from .pagination import LargePagination, SmallPagination
from .permissions import (
    CreatorPermission, OwnerPermission,
    ReadPermission, ReadWritePermission
)
from ..utils import (
    export_vocab_source, import_vocab_source
)
from .views_mixins import BatchMixin


class VocabSourceViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabSourceSerializer
    queryset = VocabSource.objects.select_related('vocab_project').prefetch_related('vocab_contexts')
    permission_classes = [ReadPermission, CreatorPermission]
    pagination_class = SmallPagination

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)

        return obj


class NestedVocabSourceViewSet(
    APIDefaultsMixin, BatchMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabSource.objects.select_related('vocab_project').prefetch_related('vocab_contexts')
    serializer_class = VocabSourceSerializer
    vocab_project = None
    permission_classes = [ReadPermission, OwnerPermission]
    pagination_class = SmallPagination

    def get_vocab_project(self, vocab_project_pk=None):
        if not self.vocab_project:
            self.vocab_project = get_object_or_404(VocabProject, id=vocab_project_pk)

        return self.vocab_project

    def get_queryset(self):
        return self.queryset.filter(vocab_project_id=self.kwargs['vocab_project_pk'])

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
