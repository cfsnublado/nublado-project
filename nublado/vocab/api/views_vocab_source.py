from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    GenericViewSet
)

from django.db.models import F, IntegerField, Value
from django.db.models.functions import Lower

from core.api.views_api import APIDefaultsMixin
from ..models import VocabContextEntry, VocabSource
from ..serializers import (
    VocabSourceSerializer, VocabSourceEntrySerializer
)
from .pagination import LargePagination, SmallPagination
from .permissions import (
    SourceCreatorPermission,
    ReadPermission, ReadWritePermission
)
from ..utils import (
    export_vocab_source, import_vocab_source
)


class VocabSourceViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = VocabSourceSerializer
    queryset = VocabSource.objects.prefetch_related("vocab_contexts")
    permission_classes = [ReadPermission, SourceCreatorPermission]
    pagination_class = SmallPagination

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj


class VocabSourceEntryViewSet(APIDefaultsMixin, ListModelMixin, GenericViewSet):
    vocab_source_pk = None
    permission_classes = [ReadWritePermission]
    pagination_class = LargePagination

    def get_queryset(self):
        language = self.request.query_params.get("language", None)
        qs = VocabContextEntry.objects.select_related("vocab_context", "vocab_entry")

        if language:
            qs = qs.filter(vocab_entry__language=language)

        qs = qs.filter(vocab_context__vocab_source_id=self.vocab_source_pk)
        qs = qs.order_by("vocab_entry__entry").distinct()
        qs = qs.values(
            language=Lower("vocab_entry__language"),
            slug=Lower("vocab_entry__slug"),
            entry=Lower("vocab_entry__entry")
        )
        qs = qs.annotate(vocab_source_id=Value(self.vocab_source_pk, output_field=IntegerField()))
        qs = qs.annotate(id=F("vocab_entry_id"))

        return qs

    def list(self, request, vocab_source_pk=None):

        if not vocab_source_pk:
            raise ParseError("Vocab source required.")
        else:
            self.vocab_source_pk = vocab_source_pk

        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = VocabSourceEntrySerializer(
                page,
                many=True,
                context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            serializer = VocabSourceEntrySerializer(
                qs,
                many=True,
                context={"request": request}
            )
            return Response(serializer.data)


class VocabSourceImportView(APIDefaultsMixin, APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        import_vocab_source(data, request.user)

        return Response(data={"success_msg": "OK!"}, status=status.HTTP_201_CREATED)


class VocabSourceExportView(APIDefaultsMixin, APIView):
    permission_classes = [
        IsAuthenticated, SourceCreatorPermission
    ]

    def get(self, request, *args, **kwargs):
        vocab_source = self.get_object()
        data = export_vocab_source(request, vocab_source)

        return Response(data=data)

    def get_object(self):
        obj = get_object_or_404(
            VocabSource.objects.prefetch_related(
                "creator",
                "vocab_contexts__vocabcontextentry_set__vocab_entry"
            ),
            id=self.kwargs["vocab_source_pk"]
        )
        self.check_object_permissions(self.request, obj)

        return obj
