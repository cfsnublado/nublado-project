from django.urls import include, path

from .views import (
    DbxView
)

app_name = "dbx"

auth_urls = [
    path(
        "dbx/",
        DbxView.as_view(),
        name="dbx"
    ),
]

urlpatterns = [
    path("auth/", include(auth_urls)),
]
