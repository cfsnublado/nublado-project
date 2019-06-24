from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs777@foo.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def get_dummy_request(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        return request
