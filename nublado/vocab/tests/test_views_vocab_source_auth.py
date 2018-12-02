import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, ListView,
    TemplateView, UpdateView
)

from core.views import AjaxDeleteMixin, MessageMixin
from core.utils import FuzzyInt
from ..conf import settings
from ..forms import VocabSourceCreateForm, VocabSourceUpdateForm
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabProject, VocabSource
)
from ..views.views_mixins import (
    VocabEntrySearchMixin, VocabProjectMixin, VocabSessionMixin,
    VocabSourceMixin
)
from ..views.views_vocab_source_auth import (
    VocabSourceEntryContextsView, VocabSourceContextsView,
    VocabSourceCreateView, VocabSourceDashboardView, VocabSourceEntriesView
)

User = get_user_model()

APP_NAME = 'vocab'
URL_PREFIX = getattr(settings, 'VOCAB_URL_PREFIX')


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
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
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def add_session_to_request(self, request):
        '''Annotate a request object with a session'''
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class VocabSourceDashboardViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceDashboardView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceDashboardView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_dashboard.html'.format(APP_NAME))


class VocabSourceEntriesViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceEntriesViewTest, self).setUp()
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is a test context. I like contexts. They are nice.'
        )
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is another test context. I like contexts. They are nice.'
        )
        self.vocab_context_3 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is yet another test context. I like contexts. They are nice.'
        )
        self.vocab_entry = VocabEntry.objects.create(entry='hello')
        self.vocab_entry_2 = VocabEntry.objects.create(entry='goodbye')

        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=self.vocab_entry_2
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_2,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_3,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_3,
            vocab_entry=self.vocab_entry_2
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            VocabEntrySearchMixin,
            TemplateView,

        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceEntriesView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceEntriesView.as_view().__name__)

    def test_view_non_authenticated_user_ed_to_login(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/source/{2}-{3}/entries/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_source.id,
                self.vocab_source.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_entries.html'.format(APP_NAME))

    def test_unique_entry_results(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        vocab_entries = response.context['vocab_entries']
        self.assertEqual(2, len(vocab_entries['en']))

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        with self.assertNumQueries(FuzzyInt(1, 10)):
            self.client.get(
                reverse(
                    'vocab:vocab_source_entries',
                    kwargs={
                        'vocab_source_pk': self.vocab_source.id,
                        'vocab_source_slug': self.vocab_source.slug
                    }
                )
            )


class VocabSourceContextsViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceContextsViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            VocabEntrySearchMixin,
            ListView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceContextsView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            'vocab:vocab_source_contexts',
            kwargs={
                'vocab_source_pk': self.vocab_source.id,
                'vocab_source_slug': self.vocab_source.slug
            }
        ))
        self.assertEqual(found.func.__name__, VocabSourceContextsView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_contexts.html'.format(APP_NAME))

    def test_view_returns_source_contexts(self):
        vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='another test source'
        )
        # Create contexts for two different sources.
        vocab_context = VocabContext.objects.create(vocab_source=self.vocab_source, content='Hello')
        VocabContext.objects.create(vocab_source=vocab_source_2, content='Hello')
        VocabContext.objects.create(vocab_source=vocab_source_2, content='Hello')

        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        vocab_contexts = response.context['vocab_contexts']
        self.assertEqual(1, vocab_contexts.count())
        self.assertEqual(vocab_contexts[0], vocab_context)

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        self.add_contexts()
        with self.assertNumQueries(FuzzyInt(1, 13)):
            self.client.get(
                reverse(
                    'vocab:vocab_source_contexts',
                    kwargs={
                        'vocab_source_pk': self.vocab_source.id,
                        'vocab_source_slug': self.vocab_source.slug
                    }
                )
            )


class VocabSourceEntryContextsViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceEntryContextsViewTest, self).setUp()
        self.vocab_entry_1 = VocabEntry.objects.create(language='es', entry='tergiversar')
        self.vocab_entry_2 = VocabEntry.objects.create(language='es', entry='demasiado')

    def add_contexts(self):
        context_text = '''Hay que tergiversar el mensaje, pero no demasiado. Demasiado sería
                          no solo confuso, sino devastador.'''
        for i in range(1, 20):
            vocab_context = VocabContext.objects.create(vocab_source=self.vocab_source, content=context_text)
            vocab_context_entry_1 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_1
            )
            vocab_context_entry_1.add_vocab_entry_tag('tergiversado')
            vocab_context_entry_2 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_2
            )
            vocab_context_entry_2.add_vocab_entry_tag('demasiado')

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            ListView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceEntryContextsView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            'vocab:vocab_source_entry_contexts',
            kwargs={
                'vocab_source_pk': self.vocab_source.id,
                'vocab_source_slug': self.vocab_source.slug,
                'vocab_entry_language': self.vocab_entry_1.language,
                'vocab_entry_slug': self.vocab_entry_1.slug
            }
        ))
        self.assertEqual(found.func.__name__, VocabSourceEntryContextsView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entry_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug,
                    'vocab_entry_language': self.vocab_entry_1.language,
                    'vocab_entry_slug': self.vocab_entry_1.slug
                }
            )
        )
        self.assertTemplateUsed(
            response,
            '{0}/auth/vocab_source_entry_contexts.html'.format(APP_NAME)
        )

    def test_view_returns_entry_contexts_from_source(self):
        self.login_test_user(self.user.username)
        self.add_contexts()
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entry_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug,
                    'vocab_entry_language': self.vocab_entry_1.language,
                    'vocab_entry_slug': self.vocab_entry_1.slug
                }
            )
        )
        qs = VocabContextEntry.objects.select_related('vocab_context__vocab_source', 'vocab_entry')
        qs = qs.prefetch_related('vocab_context__vocab_entries', 'vocab_entry_tags')
        qs = qs.filter(
            vocab_context__vocab_source_id=self.vocab_source.id,
            vocab_entry_id=self.vocab_entry_1.id
        )
        qs = qs.order_by('-date_created')
        expected_contexts = qs.all()
        contexts = response.context['vocab_entry_contexts']
        self.assertQuerysetEqual(expected_contexts, contexts, transform=lambda x: x)

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        self.add_contexts()
        with self.assertNumQueries(FuzzyInt(1, 13)):
            self.client.get(
                reverse(
                    'vocab:vocab_source_entry_contexts',
                    kwargs={
                        'vocab_source_pk': self.vocab_source.id,
                        'vocab_source_slug': self.vocab_source.slug,
                        'vocab_entry_language': self.vocab_entry_1.language,
                        'vocab_entry_slug': self.vocab_entry_1.slug
                    }
                )
            )


class VocabSourceCreateViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceCreateViewTest, self).setUp()
        self.vocab_source_data = {
            'source_type': VocabSource.BOOK,
            'name': 'A tale of two wizards',
            'description': 'Oh yeah.'
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabProjectMixin,
            MessageMixin,
            CreateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceCreateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceCreateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/project/{2}-{3}/source/create/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_project.id,
                self.vocab_project.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_create.html'.format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertIsInstance(response.context['form'], VocabSourceCreateForm)

    def test_view_injects_form_kwargs(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        form = response.context['form']
        self.assertEqual(form.creator, self.user)
        self.assertEqual(form.vocab_project, self.vocab_project)

    def test_view_creates_object(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabSource.objects.filter(
                vocab_project=self.vocab_project,
                creator=self.user,
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )
        self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        self.assertTrue(
            VocabSource.objects.filter(
                vocab_project=self.vocab_project,
                creator=self.user,
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )

    def test_invalid_data_shows_form_errors_and_does_not_save(self):
        self.vocab_source_data['name'] = ''
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VocabSource.objects.filter(
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )
        self.assertIsInstance(response.context['form'], VocabSourceCreateForm)
        self.assertFormError(response, 'form', 'name', _('validation_field_required'))

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        vocab_source = VocabSource.objects.get(
            name=self.vocab_source_data['name']
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': vocab_source.id,
                    'vocab_source_slug': vocab_source.slug
                }
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

# class UserVocabSourcesViewTest(TestCommon):

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             TemplateView,
#             VocabSessionMixin
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(UserVocabSourcesView, class_name))

#     def test_correct_view_used(self):
#         found = resolve(
#             reverse('vocab:user_vocab_sources')
#         )
#         self.assertEqual(found.func.__name__, UserVocabSourcesView.as_view().__name__)

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse('vocab:user_vocab_sources')
#         )
#         self.assertTemplateUsed(response, '{0}/admin/user_vocab_sources.html'.format(APP_NAME))

#     def test_view_shows_only_users_sources(self):
#         source_type = VocabSource.CREATED
#         user_2 = User.objects.create_user(
#             username='kfl7',
#             first_name='Karen',
#             last_name='Fuentes',
#             email='kfl7@foo.com',
#             password=self.pwd
#         )
#         for x in range(0, 4):
#             VocabSource.objects.create(
#                 creator=self.user,
#                 name='source {0}'.format(x),
#                 source_type=source_type
#             )
#         for x in range(0, 2):
#             VocabSource.objects.create(
#                 creator=user_2,
#                 name='hello {0}'.format(x),
#                 source_type=source_type
#             )
#         # user with 4 sources
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse('vocab:user_vocab_sources')
#         )
#         sources = response.context['vocab_sources']
#         self.assertEqual(len(sources[source_type]), 4)

#         # user_2 with 2 sources
#         self.login_test_user(user_2.username)
#         response = self.client.get(
#             reverse('vocab:user_vocab_sources')
#         )
#         sources = response.context['vocab_sources']
#         self.assertEqual(len(sources[source_type]), 2)


# class VocabSourceUpdateViewTest(TestCommon):

#     def setUp(self):
#         super(VocabSourceUpdateViewTest, self).setUp()
#         self.vocab_source = VocabSource.objects.create(
#             creator=self.user,
#             source_type=VocabSource.BOOK,
#             name='A good book'
#         )

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             VocabSourceMixin,
#             UpdateView
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(VocabSourceUpdateView, class_name))

#     def test_correct_view_used(self):
#         found = resolve(
#             reverse(
#                 'vocab:vocab_source_update',
#                 kwargs={'pk': self.vocab_source.id}
#             )
#         )
#         self.assertEqual(found.func.__name__, VocabSourceUpdateView.as_view().__name__)

#     def test_view_non_authenticated_user_redirected_to_login(self):
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_source_update',
#                 kwargs={'pk': self.vocab_source.id}
#             )
#         )
#         self.assertRedirects(
#             response,
#             expected_url='{0}?next=/admin/{1}/source/{2}/update/'.format(
#                 reverse(settings.LOGIN_URL),
#                 URL_PREFIX,
#                 self.vocab_source.id
#             ),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_returns_correct_status_code(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_source_update',
#                 kwargs={'pk': self.vocab_source.id}
#             )
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_source_update',
#                 kwargs={'pk': self.vocab_source.id}
#             )
#         )
#         self.assertTemplateUsed(response, '{0}/admin/vocab_source_update.html'.format(APP_NAME))

#     def test_view_uses_correct_form(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_source_update',
#                 kwargs={'pk': self.vocab_source.id}
#             )
#         )
#         self.assertIsInstance(response.context['form'], VocabSourceUpdateForm)


# class VocabSourceDeleteViewTest(TestCommon):

#     def setUp(self):
#         super(VocabSourceDeleteViewTest, self).setUp()
#         self.vocab_source = VocabSource.objects.create(
#             creator=self.user,
#             source_type=VocabSource.BOOK,
#             name='A good book'
#         )

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             AjaxDeleteMixin,
#             DeleteView
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(VocabSourceDeleteView, class_name))

#     def test_correct_view_used(self):
#         found = resolve(reverse(
#             'vocab:vocab_source_delete',
#             kwargs={'pk': self.vocab_source.id})
#         )
#         self.assertEqual(found.func.__name__, VocabSourceDeleteView.as_view().__name__)

#     def test_view_non_authenticated_user_redirected_to_login(self):
#         response = self.client.get(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': self.vocab_source.id})
#         )
#         self.assertRedirects(
#             response,
#             expected_url='{url}?next=/admin/{module}/source/{pk}/delete/'.format(
#                 url=reverse(settings.LOGIN_URL),
#                 module=URL_PREFIX,
#                 pk=self.vocab_source.id
#             ),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_returns_correct_status_code(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': self.vocab_source.id})
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': self.vocab_source.id})
#         )
#         self.assertTemplateUsed(response, '{0}/admin/vocab_source_delete_confirm.html'.format(APP_NAME))

#     def test_view_deletes_object(self):
#         self.login_test_user(self.user.username)
#         obj_id = self.vocab_source.id
#         self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
#         self.client.post(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': obj_id})
#         )
#         self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())

#     def test_view_redirects_on_success(self):
#         self.login_test_user(self.user.username)
#         response = self.client.post(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': self.vocab_source.id})
#         )
#         self.assertRedirects(
#             response,
#             expected_url=reverse('vocab:user_vocab_sources'),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_ajax(self):
#         self.login_test_user(self.user.username)
#         kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
#         obj_id = self.vocab_source.id
#         self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
#         response = self.client.post(
#             reverse('vocab:vocab_source_delete', kwargs={'pk': obj_id}),
#             **kwargs
#         )
#         self.assertEqual(response.status_code, 200)
#         json_string = response.content.decode('utf-8')
#         response_data = json.loads(json_string)
#         self.assertEqual(_('message_success'), response_data['success_message'])
#         self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())


# class VocabSourceContextEntriesViewTest(TestCommon):

#     def setUp(self):
#         super(VocabSourceContextEntriesViewTest, self).setUp()
#         self.vocab_source = VocabSource.objects.create(
#             creator=self.user,
#             source_type=VocabSource.BOOK,
#             name='A good book'
#         )
#         self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user, language='es', entry='tergiversar')
#         self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, language='es', entry='demasiado')

#     def add_contexts(self):
#         context_text = '''Hay que tergiversar el mensaje, pero no demasiado. Demasiado sería
#                           no solo confuso, sino devastador.'''
#         for i in range(1, 20):
#             vocab_context = VocabContext.objects.create(
#                 vocab_source=self.vocab_source,
#                 content=context_text
#             )
#             vocab_context_entry_1 = VocabContextEntry.objects.create(
#                 vocab_context=vocab_context,
#                 vocab_entry=self.vocab_entry_1
#             )
#             vocab_context_entry_1.add_vocab_entry_tag('demasiado')
#             vocab_context_entry_2 = VocabContextEntry.objects.create(
#                 vocab_context=vocab_context,
#                 vocab_entry=self.vocab_entry_2
#             )
#             vocab_context_entry_2.add_vocab_entry_tag('demasiado')

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             VocabSourceMixin,
#             ListView
#         )
#         for class_name in classes:
#             self.assertTrue(
#                 issubclass(VocabSourceContextEntriesView, class_name)
#             )

#     def test_correct_view_used(self):
#         found = resolve(reverse(
#             'vocab:vocab_source_context_entries',
#             kwargs={
#                 'vocab_source_pk': self.vocab_source.id,
#                 'language': self.vocab_entry_1.language,
#                 'vocab_entry_slug': self.vocab_entry_1.slug
#             })
#         )
#         self.assertEqual(
#             found.func.__name__, VocabSourceContextEntriesView.as_view().__name__
#         )

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_source_context_entries',
#                 kwargs={
#                     'vocab_source_pk': self.vocab_source.id,
#                     'language': self.vocab_entry_1.language,
#                     'vocab_entry_slug': self.vocab_entry_1.slug
#                 }
#             )
#         )
#         self.assertTemplateUsed(
#             response,
#             '{0}/admin/vocab_source_context_entries.html'.format(APP_NAME)
#         )

#     def test_num_queries(self):
#         self.login_test_user(self.user.username)
#         self.add_contexts()
#         with self.assertNumQueries(FuzzyInt(1, 11)):
#             self.client.get(
#                 reverse(
#                     'vocab:vocab_source_context_entries',
#                     kwargs={
#                         'vocab_source_pk': self.vocab_source.id,
#                         'language': self.vocab_entry_1.language,
#                         'vocab_entry_slug': self.vocab_entry_1.slug
#                     }
#                 )
#             )


# class ExportVocabSourceJsonViewTest(TestCommon):

#     def test_export_source_json_to_file(self):
#         pass
