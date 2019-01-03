from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication, TokenAuthentication
)
from rest_framework.permissions import IsAuthenticated


class APIDefaultsMixin(object):
    """
    Default settings for view authentication, permissions,
    filtering and pagination.
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication
    ]
    permission_classes = [IsAuthenticated]
    paginate_by = 25
