from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView

from .views import (
    AppSessionView, HomeView
)

app_name = "app"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("app-session/", AppSessionView.as_view(), name="app_session"),

]

if settings.DEBUG:
    urlpatterns += [
        path("404", TemplateView.as_view(template_name="404.html"))
    ]
