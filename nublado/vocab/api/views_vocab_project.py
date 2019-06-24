from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from core.api.views_api import APIDefaultsMixin
from ..models import VocabProject
from ..serializers import VocabProjectSerializer
from .pagination import SmallPagination
from .permissions import ReadPermission, ProjectOwnerPermission


class VocabProjectViewSet(APIDefaultsMixin, ModelViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabProjectSerializer
    queryset = VocabProject.objects.all()
    permission_classes = [ReadPermission, ProjectOwnerPermission]
    pagination_class = SmallPagination

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
