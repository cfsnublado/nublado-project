from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, username=None, email=None, password=None, **kwargs):
        if not username:
            raise ValueError(_('validation_username_required'))
        if not email:
            raise ValueError(_('validation_email_required'))
        user = self.model(
            username=username.lower(),
            email=email.lower(),
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, email=None, password=None, **kwargs):
        user = self.create_user(username=username, email=email, password=password, **kwargs)
        user.is_admin = True
        user.is_superuser = True
        user.clean()
        user.save(using=self._db)
        return user

    def create_inactive_incomplete_user(self, username=None, email=None, **kwargs):
        if not username:
            raise ValueError(_('validation_username_required'))
        if not email:
            raise ValueError(_('validation_email_required'))
        user = self.model(
            username=username,
            email=email.lower(),
            is_active=False,
            **kwargs
        )
        user.clean()
        user.save(using=self._db)
        return user

    def create(self, username=None, email=None, password=None, **kwargs):
        return self.create_user(username=username, email=email, password=password, **kwargs)

    def get_queryset(self):
        return super(UserManager, self).get_queryset().select_related('profile')
