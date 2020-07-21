from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet
)

from core.api.views_api import APIDefaultsMixin
from ..conf import settings
from ..models import VocabEntry
from ..serializers import (
    VocabEntrySerializer
)
from .pagination import LargePagination
from .permissions import (
    IsSuperuser, ReadWritePermission
)
from ..utils import (
    export_vocab_entries, get_oxford_entry_json,
    get_random_vocab_entry, import_vocab_entries,
    parse_oxford_entry_json
)
from .views_mixins import BatchMixin

OXFORD_API_ID = getattr(settings, "OXFORD_API_ID", None)
OXFORD_API_KEY = getattr(settings, "OXFORD_API_KEY", None)


class VocabEntryViewSet(APIDefaultsMixin, BatchMixin, ModelViewSet):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = VocabEntrySerializer
    permission_classes = [ReadWritePermission]
    pagination_class = LargePagination

    def get_queryset(self):
        language = self.request.query_params.get("language", None)
        qs = VocabEntry.objects.order_by("entry")

        if language:
            qs = qs.filter(language=language)

        return qs

    @action(methods=["get"], detail=False)
    def detail_data(self, request):
        """
        Retrieve VocabEntry object
        """
        entry = request.query_params.get("entry", None)
        language = request.query_params.get("language", "en")

        if not entry:
            raise ParseError("Vocab entry required.")

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

    @action(methods=["get"], detail=False)
    def random_detail_data(self, request):
        """
        Retrieve random VocabEntry object
        """
        language = request.query_params.get("language", None)

        vocab_entry = get_random_vocab_entry(language=language)

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

        if "vocab_entries" in data:
            import_vocab_entries(data)
            return Response(data={"success_msg": "OK!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={"error": "vocab-data required"}, status=status.HTTP_400_BAD_REQUEST)


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
            language=kwargs["language"]
        )

        return Response(data=data)


class VocabEntryInfoView(APIView):
    vocab_entry = None

    def get_vocab_entry(self, vocab_entry_pk=None):
        if not self.vocab_entry:
            self.vocab_entry = get_object_or_404(VocabEntry, id=vocab_entry_pk)

    def get(self, request, *args, **kwargs):
        self.get_vocab_entry(kwargs["vocab_entry_pk"])
        result_data = {}
        json_data = get_oxford_entry_json(
            OXFORD_API_ID,
            OXFORD_API_KEY,
            self.vocab_entry
        )

        if json_data:
            result_data = parse_oxford_entry_json(
                json_data, language=self.vocab_entry.language
            )

            return Response(data=result_data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
