from django.urls import re_path

from .views import serve_docs

app_name = "appdocs"

urlpatterns = [
    re_path(
        "^(?P<path>.*)$", serve_docs
    ),
]
