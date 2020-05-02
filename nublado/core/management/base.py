import getpass

from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand, CommandError


class LoginCommand(BaseCommand):

    def login_user(self):
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        user = authenticate(username=username, password=password)

        if user is not None:
            return user
        else:
            raise CommandError('Invalid login')
