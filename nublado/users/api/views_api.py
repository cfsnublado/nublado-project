from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from core.api.views_api import APIDefaultsMixin
from ..models import User, Profile
from ..serializers import UserSerializer, ProfileSerializer


class UserViewSet(APIDefaultsMixin, ModelViewSet):

    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    lookup_value_regex = "[\w.@+-]+"
    queryset = User.objects.select_related("profile").order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    permission_classes = [
        IsAdminUser
    ]


class ProfileViewSet(APIDefaultsMixin, ModelViewSet):

    lookup_field = "user__username"
    lookup_url_kwarg = "username"
    lookup_value_regex = "[\w.@+-]+"
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [
        IsAdminUser
    ]
