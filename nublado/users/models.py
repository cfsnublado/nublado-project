from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import SerializeModel, TimestampModel, UUIDModel
from .conf import settings
from .managers import UserManager
from .validation import (
    email_format, name_characters, username_characters,
    username_min_length
)


class User(
    UUIDModel, TimestampModel, PermissionsMixin,
    SerializeModel, AbstractBaseUser
):
    username = models.CharField(
        verbose_name=_("label_username"),
        max_length=50,
        unique=True,
        validators=[username_min_length, username_characters]
    )
    email = models.EmailField(
        verbose_name=_("label_email"),
        max_length=50,
        unique=True,
        validators=[email_format],
        error_messages={"unique": _("validation_email_unique")}
    )
    first_name = models.CharField(
        verbose_name=_("label_first_name"),
        max_length=100,
        validators=[name_characters]
    )
    last_name = models.CharField(
        verbose_name=_("label_last_name"),
        max_length=100,
        validators=[name_characters]
    )
    is_active = models.BooleanField(
        verbose_name=_("label_is_active"),
        default=False
    )
    is_admin = models.BooleanField(
        verbose_name=_("label_is_admin"),
        default=False
    )

    objects = UserManager()
    USERNAME_FIELD = "username"

    def __str__(self):
        return "{0} : {1}".format(self.email, self.get_full_name())

    def get_absolute_url(self):
        return reverse("users:profile_view", args=[self.username])

    def clean(self, *args, **kwargs):
        self.email = self.email.lower()
        self.username = self.username.lower()

    @property
    def is_staff(self):
        return self.is_admin

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def get_serializer(self):
        from .serializers import UserSerializer
        return UserSerializer


class Profile(TimestampModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("label_user")
    )
    about = models.TextField(
        verbose_name=_("label_profile_about"),
        blank=True
    )
    avatar_url = models.URLField(
        verbose_name=_("label_avatar_url"),
        blank=True
    )

    @property
    def username(self):
        return self.user.username

    class Meta:
        verbose_name = _("label_profile")
        verbose_name_plural = _("label_profile_plural")
        ordering = ("user",)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return self.user.get_absolute_url()

    def get_serializer(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer
