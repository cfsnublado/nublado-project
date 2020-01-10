from django.urls import path, re_path

from .views import (
    ProfileDetailView,
    UserForgotPasswordRequestView, UserForgotPasswordResetView
)
from .views_auth import UserPasswordResetView

app_name = "users"

urlpatterns = [
    path(
        "<slug:username>",
        ProfileDetailView.as_view(),
        name="profile_view"
    ),
    path(
        "forgot-password/",
        UserForgotPasswordRequestView.as_view(),
        name="user_password_reset_request"
    ),
    re_path(
        r"^forgot-password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        UserForgotPasswordResetView.as_view(),
        name="user_forgot_password_reset"
    ),
    path(
        "update/<slug:username>/password-reset/",
        UserPasswordResetView.as_view(),
        name="user_password_reset"
    )
]
