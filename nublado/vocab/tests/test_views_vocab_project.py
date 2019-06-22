from django.contrib.auth import get_user_model
from django.test import TestCase
from django.views.generic import TemplateView
from django.urls import resolve, reverse

from core.views import ObjectSessionMixin
from ..models import VocabProject
from ..views.views_mixins import (
    VocabProjectMixin, VocabProjectSessionMixin
)
from ..views.views_vocab_project import (
    VocabProjectsView, VocabProjectDashboardView
)

User = get_user_model()

APP_NAME = 'vocab'


class TestCommon(TestCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.pwd = 'Coffee?69c'
        self.user = User.objects.create_superuser(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabProjectsViewTest(TestCommon):

    def setUp(self):
        super(VocabProjectsViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            ObjectSessionMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabProjectsView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('vocab:vocab_projects'))
        self.assertEqual(found.func.__name__, VocabProjectsView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('vocab:vocab_projects'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('vocab:vocab_projects'))
        self.assertTemplateUsed(response, '{0}/vocab_projects.html'.format(APP_NAME))


class VocabProjectDashboardViewTest(TestCommon):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )

    def test_inheritance(self):
        classes = (
            VocabProjectMixin,
            VocabProjectSessionMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabProjectDashboardView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_project_dashboard',
                kwargs={
                    'vocab_project_pk': self.vocab_project.pk,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabProjectDashboardView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_project_dashboard',
                kwargs={
                    'vocab_project_pk': self.vocab_project.pk,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_project_dashboard',
                kwargs={
                    'vocab_project_pk': self.vocab_project.pk,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )

        self.assertTemplateUsed(response, '{0}/vocab_project_dashboard.html'.format(APP_NAME))
