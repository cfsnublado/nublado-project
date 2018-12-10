from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import FunctionalTest, page_titles, DEFAULT_PWD, PROJECT_NAME
from vocab.models import (
    VocabEntry, VocabContext, VocabProject, VocabSource
)

User = get_user_model()

page_titles.update({
    'page_vocab_entry_search_title_en': '{0} | {1}'.format('Search vocabulary', PROJECT_NAME),
    'page_vocab_user_dashboard_title_en': '{0} | {1}'.format('Vocabulary dashboard', PROJECT_NAME)
})


class TestCommon(FunctionalTest):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@cfs.com',
            password=DEFAULT_PWD
        )
        self.project = VocabProject.objects.create(
            owner=self.user,
            name='Test project',
            description='A test project'
        )


class VocabEntrySearchTest(TestCommon):

    def setUp(self):
        super(VocabEntrySearchTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.project,
            creator=self.user,
            source_type=VocabSource.CREATED,
            name='Una prueba'
        )
        self.vocab_entry_es = VocabEntry.objects.create(language='es', entry='comer')
        context_text_es = 'A ella le gusta comer pizza los domingos.'
        self.vocab_context_es = VocabContext.objects.create(vocab_source=self.vocab_source, content=context_text_es)

    def test_vocab_entry_search(self):
        self.browser.get('{0}{1}'.format(
            self.live_server_url,
            reverse('vocab:vocab_entry_search'))
        )
        self.page_load(page_titles['page_vocab_entry_search_title_en'])
        search_language = 'es'
        link = self.search_autocomplete_by_language(search_language, self.vocab_entry_es.entry)
        link.click()
        self.page_load(page_titles['page_vocab_entry_search_title_en'])
        url = '{0}{1}?search_entry={2}&search_language={3}'.format(
            self.live_server_url,
            reverse('vocab:vocab_entry_search'),
            self.vocab_entry_es.entry,
            search_language
        )
        self.assertEqual(url, self.browser.current_url)
        header = self.get_element_by_id('vocab-entry-header')
        self.assertEqual(header.text, self.vocab_entry_es.entry)


class VocabEntryAuthTest(TestCommon):

    def test_create_entry(self):
        self.browser.get('{0}{1}'.format(
            self.live_server_url,
            reverse('vocab:vocab_user_dashboard'))
        )
        self.login_user(self.user.username)
        self.page_load(page_titles['page_vocab_user_dashboard_title_en'])
        self.open_sidebar()
        self.open_modal(
            trigger_id='sidebar-nav-vocab-entry-create',
            modal_id='create-entry-modal'
        )
