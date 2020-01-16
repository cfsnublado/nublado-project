from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import FunctionalTest, page_titles, DEFAULT_PWD, PROJECT_NAME
from vocab.models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabEntryTag, VocabSource
)

User = get_user_model()

page_titles.update({
    "vocab_entry_en": "Vocabulary - {0} | {1}",
    "vocab_entries_en": "{0} | {1}".format("Vocabulary", PROJECT_NAME),
    "vocab_entry_create_en": "{0} | {1}".format("Create vocab entry", PROJECT_NAME),
    "vocab_entry_update_en": "{0} | {1}".format("Edit vocab entry", PROJECT_NAME),
    "vocab_sources_en": "{0} | {1}".format("Sources", PROJECT_NAME),
    "vocab_source_entry_en": "{0} - {1} | {2}",
    "vocab_source_contexts_en": "{0} - Contexts | {1}",
    "vocab_source_create_en": "{0} | {1}".format("Create source", PROJECT_NAME),
    "vocab_source_update_en": "{0} | {1}".format("Edit source", PROJECT_NAME),
    "vocab_context_create_en": "{0} | {1}".format("Create context", PROJECT_NAME),
    "vocab_context_update_en": "{0} | {1}".format("Edit context", PROJECT_NAME),
})


class TestCommon(FunctionalTest):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.superuser = User.objects.create_superuser(
            username="cfs",
            first_name="Christopher",
            last_name="Sand",
            email="cfs@cfs.com",
            password=DEFAULT_PWD
        )
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@cfs.com",
            password=DEFAULT_PWD
        )


class VocabEntrySearchTest(TestCommon):

    def setUp(self):
        super(VocabEntrySearchTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="comer"
        )

    def test_vocab_entry_search(self):
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_entries"))
        )
        self.load_page(page_titles["vocab_entries_en"])

        # Not found
        search_language = "en"
        search_term = "foo"
        self.search_click_by_language(language=search_language, search_text=search_term)
        self.load_page(page_titles["vocab_entries_en"])
        url = '{0}{1}?search_entry={2}&search_language={3}'.format(
            self.live_server_url,
            reverse("vocab:vocab_entries"),
            search_term,
            search_language
        )
        self.assertEqual(url, self.browser.current_url)

        # Found
        link = self.search_autocomplete_by_language(
            self.vocab_entry.language,
            self.vocab_entry.entry
        )
        link.click()
        self.load_page("{0} - {1} | {2}".format(
            "Vocabulary",
            self.vocab_entry.entry,
            PROJECT_NAME)
        )
        url = "{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            ),
        )
        self.assertEqual(url, self.browser.current_url)
        header = self.get_element_by_id("vocab-entry-header")
        self.assertEqual(header.text, self.vocab_entry.entry)


class VocabEntryAuthTest(TestCommon):

    def setUp(self):
        super(VocabEntryAuthTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )

    def fill_vocab_entry_form(
        self, entry=None, language=None
    ):
        if entry is not None:
            entry_input = self.get_element_by_id("id_entry")
            entry_input.clear()
            entry_input.send_keys(entry)

        if language is not None:
            language_select = Select(self.get_element_by_id("id_language"))
            language_select.select_by_value(language)

        self.get_submit_button().click()

    def test_create_vocab_entry(self):
        vocab_entry_data = {
            "language": "es",
            "entry": "trastabillar"
        }

        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data["language"],
                entry=vocab_entry_data["entry"]
            ).exists()
        )

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("app:home"))
        )
        self.get_login_link().click()
        self.login_user(self.superuser.username)
        self.load_page(page_titles["home_en"])

        self.get_user_toggle().click()
        self.get_element_by_id("user-nav-new-entry").click()
        self.load_page(page_titles["vocab_entry_create_en"])
        self.fill_vocab_entry_form(
            language=vocab_entry_data["language"],
            entry=vocab_entry_data["entry"]
        )
        self.load_page("{0} - {1} | {2}".format(
            "Vocabulary",
            vocab_entry_data["entry"],
            PROJECT_NAME)
        )

        self.assertTrue(
            VocabEntry.objects.filter(
                language=vocab_entry_data["language"],
                entry=vocab_entry_data["entry"]
            ).exists()
        )

    def test_update_vocab_entry(self):
        vocab_entry_data = {
            "language": "en",
            "entry": "dog"
        }

        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data["language"],
                entry=vocab_entry_data["entry"]
            ).exists()
        )

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry_update",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            )
        ))
        self.login_user(self.superuser.username)
        self.load_page(page_titles["vocab_entry_update_en"])

        self.fill_vocab_entry_form(
            language=vocab_entry_data["language"],
            entry=vocab_entry_data["entry"]
        )
        self.vocab_entry.refresh_from_db()

        self.assertEqual(self.vocab_entry.language, vocab_entry_data["language"])
        self.assertEqual(self.vocab_entry.entry, vocab_entry_data["entry"])

    def test_delete_vocab_entry(self):
        # Delete from vocab entry update page.
        vocab_entry_id = self.vocab_entry.id

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry_update",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            )
        ))
        self.login_user(self.superuser.username)
        self.load_page(page_titles["vocab_entry_update_en"])

        self.open_modal(
            trigger_id="vocab-entry-delete-btn",
            modal_id="delete-vocab-entry"
        )
        self.get_element_by_id("vocab-entry-delete-ok").click()
        self.load_page(page_titles["vocab_entries_en"])

        self.assertFalse(
            VocabEntry.objects.filter(id=vocab_entry_id).exists()
        )

        # Delete from vocab entries page.
        self.vocab_entry = VocabEntry.objects.create(language="en", entry="unbeknownst")
        vocab_entry_id = self.vocab_entry.id

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_entries")
        ))
        self.load_page(page_titles["vocab_entries_en"])

        vocab_entry_tag = "#entry-{0}".format(self.vocab_entry.id)
        vocab_entry_tag_delete = "{0} .delete-btn".format(vocab_entry_tag)

        self.get_element_by_css(vocab_entry_tag_delete).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "vocab-entry-delete-ok")))
        self.get_element_by_id("vocab-entry-delete-ok").click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, vocab_entry_tag)))

        self.assertFalse(VocabEntry.objects.filter(id=vocab_entry_id).exists())


class VocabSourceAuthTest(TestCommon):

    def setUp(self):
        super(VocabSourceAuthTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.CREATED,
            name="Test source",
            description="This is a test source."
        )

    def fill_vocab_source_form(
        self, source_type=None, name=None, description=None
    ):
        if source_type is not None:
            source_type_select = Select(self.get_element_by_id("id_source_type"))
            source_type_select.select_by_value(source_type)

        if name is not None:
            name_input = self.get_element_by_id("id_name")
            name_input.clear()
            name_input.send_keys(name)

        if description is not None:
            description_textarea = self.get_element_by_id("id_description")
            description_textarea.clear()
            description_textarea.send_keys(description)

        self.get_submit_button().click()

    def test_create_vocab_source(self):
        vocab_source_data = {
            "source_type": VocabSource.CREATED,
            "name": "Another test source",
            "description": "This is another test source."
        }

        self.assertFalse(
            VocabSource.objects.filter(
                source_type=vocab_source_data["source_type"],
                name=vocab_source_data["name"],
                description=vocab_source_data["description"]
            ).exists()
        )

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("app:home"))
        )
        self.get_login_link().click()
        self.login_user(self.user.username)
        self.load_page(page_titles["home_en"])

        self.get_user_toggle().click()
        self.get_element_by_id("user-nav-new-source").click()
        self.load_page(page_titles["vocab_source_create_en"])
        self.fill_vocab_source_form(
            source_type=str(vocab_source_data["source_type"]),
            name=vocab_source_data["name"],
            description=vocab_source_data["description"]
        )
        self.load_page("{0} | {1}".format(vocab_source_data["name"], PROJECT_NAME))

        self.assertTrue(
            VocabSource.objects.filter(
                source_type=vocab_source_data["source_type"],
                name=vocab_source_data["name"],
                description=vocab_source_data["description"]
            ).exists()
        )

    def test_update_vocab_source(self):
        vocab_source_data = {
            "source_type": VocabSource.BOOK,
            "name": "Foo",
            "description": "Lorem ipsum"
        }

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_source_update",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        ))
        self.login_user(self.user.username)
        self.load_page(page_titles["vocab_source_update_en"])

        self.fill_vocab_source_form(
            source_type=str(vocab_source_data["source_type"]),
            name=vocab_source_data["name"],
            description=vocab_source_data["description"]
        )
        self.vocab_source.refresh_from_db()

        self.assertEqual(self.vocab_source.source_type, vocab_source_data["source_type"])
        self.assertEqual(self.vocab_source.name, vocab_source_data["name"])
        self.assertEqual(self.vocab_source.description, vocab_source_data["description"])

    def test_delete_vocab_source(self):
        # Delete from vocab source update page.
        vocab_source_id = self.vocab_source.id

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_source_update",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        ))
        self.login_user(self.superuser.username)
        self.load_page(page_titles["vocab_source_update_en"])

        self.open_modal(
            trigger_id="vocab-source-delete-btn",
            modal_id="delete-vocab-source"
        )
        self.get_element_by_id("vocab-source-delete-ok").click()
        self.load_page(page_titles["vocab_sources_en"])

        self.assertFalse(
            VocabSource.objects.filter(id=vocab_source_id).exists()
        )

        # Delete from vocab sources page.
        self.vocab_source = VocabSource.objects.create(
            creator=self.superuser,
            source_type=VocabSource.BOOK,
            name="Una fuente",
            description="Una nueva fuente"
        )
        vocab_source_id = self.vocab_source.id

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_sources")
        ))
        self.load_page(page_titles["vocab_sources_en"])

        vocab_source_box = "#source-{0}".format(self.vocab_source.id)
        vocab_source_box_delete = "{0} .delete-btn".format(vocab_source_box)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vocab_source_box)))
        self.get_element_by_css(vocab_source_box_delete).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "vocab-source-delete-ok")))
        self.get_element_by_id("vocab-source-delete-ok").click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, vocab_source_box)))

        self.assertFalse(VocabSource.objects.filter(id=vocab_source_id).exists())


class VocabContextTest(TestCommon):
    def setUp(self):
        super(VocabContextTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="content"
        )
        self.vocab_source = VocabSource.objects.create(
            creator=self.superuser,
            source_type=VocabSource.CREATED,
            name="Test source",
            description="This is a test source."
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is the context's content. Each context has content."
        )
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context
        )
        VocabEntryTag.objects.create(
            vocab_context_entry=self.vocab_context_entry,
            content="content"
        )

    def get_highlight_xpath(self, tag, context_text_id):
        xpath = "//mark[@class='tagged-text' and contains(., '{0}') and ancestor::div[@id='{1}']]".format(
            tag,
            context_text_id
        )
        return xpath

    def test_view_tagged_context(self):
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            )
        ))
        self.load_page(
            page_titles["vocab_entry_en"].format(self.vocab_entry.entry, PROJECT_NAME)
        )

        vocab_context_box = "#context-{0}".format(self.vocab_context.id)
        vocab_context_text_id = "context-{0}-text".format(self.vocab_context.id)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vocab_context_box)))

        # Vocab entry instance is highlighted in text.
        vocab_entry_highlight_xp = self.get_highlight_xpath(
            tag=self.vocab_entry.entry,
            context_text_id=vocab_context_text_id
        )
        vocab_entry_highlighted = self.get_elements_by_xpath(vocab_entry_highlight_xp)

        self.assertEqual(len(vocab_entry_highlighted), 2)


class VocabContextAuthTest(TestCommon):
    def setUp(self):
        super(VocabContextAuthTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="context"
        )
        self.vocab_source = VocabSource.objects.create(
            creator=self.superuser,
            source_type=VocabSource.CREATED,
            name="Test source",
            description="This is a test source."
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        VocabContextEntry.objects.create(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context
        )

    def fill_vocab_context_form(self, content=None):
        if content is not None:
            content_textarea = self.get_element_by_id("id_content")
            content_textarea.clear()
            content_textarea.send_keys(content)

        self.get_submit_button().click()

    def test_create_vocab_context(self):
        vocab_context_data = {
            "content": "The cat walked across the room."
        }

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_source_dashboard",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        ))
        self.get_login_link().click()
        self.login_user(self.superuser.username)
        self.load_page("{0} | {1}".format(self.vocab_source.name, PROJECT_NAME))

        self.open_sidebar()
        self.get_element_by_id("sidebar-new-vocab-context").click()
        self.load_page(page_titles["vocab_context_create_en"])
        self.fill_vocab_context_form(content=vocab_context_data["content"])
        self.load_page(page_titles["vocab_context_update_en"])

    def test_delete_vocab_context(self):
        # Delete from entry contexts
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            )
        ))
        self.get_login_link().click()
        self.login_user(self.superuser.username)
        self.load_page(
            page_titles["vocab_entry_en"].format(self.vocab_entry.entry, PROJECT_NAME)
        )

        vocab_context_id = self.vocab_context.id
        vocab_context_box = "#context-{0}".format(self.vocab_context.id)
        vocab_context_box_delete = "{0} .delete-btn".format(vocab_context_box)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vocab_context_box)))
        self.get_element_by_css(vocab_context_box_delete).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "vocab-context-delete-ok")))
        self.get_element_by_id("vocab-context-delete-ok").click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, vocab_context_box)))

        self.assertFalse(VocabContext.objects.filter(id=vocab_context_id).exists())

        # Delete from source entry contexts
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        VocabContextEntry.objects.create(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context
        )

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_source_entry",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug,
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            )
        ))
        self.load_page(
            page_titles["vocab_source_entry_en"].format(
                self.vocab_source.name,
                self.vocab_entry.entry,
                PROJECT_NAME
            )
        )

        vocab_context_id = self.vocab_context.id
        vocab_context_box = "#context-{0}".format(self.vocab_context.id)
        vocab_context_box_delete = "{0} .delete-btn".format(vocab_context_box)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vocab_context_box)))
        self.get_element_by_css(vocab_context_box_delete).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "vocab-context-delete-ok")))
        self.get_element_by_id("vocab-context-delete-ok").click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, vocab_context_box)))

        self.assertFalse(VocabContext.objects.filter(id=vocab_context_id).exists())

        # Delete from source contexts
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        VocabContextEntry.objects.create(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context
        )

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_source_contexts",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug,
                }
            )
        ))
        self.load_page(
            page_titles["vocab_source_contexts_en"].format(
                self.vocab_source.name,
                PROJECT_NAME
            )
        )

        vocab_context_id = self.vocab_context.id
        vocab_context_box = "#context-{0}".format(self.vocab_context.id)
        vocab_context_box_delete = "{0} .delete-btn".format(vocab_context_box)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vocab_context_box)))
        self.get_element_by_css(vocab_context_box_delete).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "vocab-context-delete-ok")))
        self.get_element_by_id("vocab-context-delete-ok").click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, vocab_context_box)))

        self.assertFalse(VocabContext.objects.filter(id=vocab_context_id).exists())
