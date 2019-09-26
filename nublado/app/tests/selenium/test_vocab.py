from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import FunctionalTest, page_titles, DEFAULT_PWD, PROJECT_NAME
from vocab.models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabSource
)

User = get_user_model()

page_titles.update({
    "vocab_entry_search_en": "{0} | {1}".format("Vocabulary", PROJECT_NAME),
    "vocab_user_dashboard_en": "{0} | {1}".format("Vocabulary dashboard", PROJECT_NAME),
    "vocab_context_tag_en": "{0} | {1}".format("Edit context", PROJECT_NAME),
    "vocab_entries_en": "{0} | {1}".format("Vocabulary", PROJECT_NAME),
    "vocab_entry_update_en": "{0} | {1}".format("Edit entry", PROJECT_NAME)
})


class TestCommon(FunctionalTest):

    def setUp(self):
        super(TestCommon, self).setUp()
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
        self.vocab_entry_es = VocabEntry.objects.create(
            language="es",
            entry="comer"
        )

    def test_vocab_entry_search(self):
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_entries"))
        )
        self.load_page(page_titles["vocab_entry_search_en"])
        search_language = "es"
        link = self.search_autocomplete_by_language(search_language, self.vocab_entry_es.entry)
        link.click()
        self.load_page("{0} - {1} | {2}".format("Vocabulary", self.vocab_entry_es.entry, PROJECT_NAME))
        url = "{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_entry",
                kwargs={
                    "vocab_entry_language": self.vocab_entry_es.language,
                    "vocab_entry_slug": self.vocab_entry_es.slug
                }
            ),
        )
        self.assertEqual(url, self.browser.current_url)
        header = self.get_element_by_id("vocab-entry-header")
        self.assertEqual(header.text, self.vocab_entry_es.entry)


class VocabEntryAuthTest(TestCommon):

    def setUp(self):
        super(VocabEntryAuthTest, self).setUp()
        self.vocab_entry_es = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )

    def test_create_entry(self):
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_user_dashboard"))
        )
        self.login_user(self.user.username)
        self.load_page(page_titles["vocab_user_dashboard_en"])
        self.open_sidebar()
        self.open_modal(
            trigger_id="sidebar-nav-vocab-entry-create",
            modal_id="create-entry-modal"
        )

    def test_entries(self):
        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse("vocab:vocab_entries"))
        )
        self.login_user(self.user.username)
        self.load_page(page_titles["vocab_entries_en"])
        search_language = "es"
        self.search_autocomplete_by_language(search_language, self.vocab_entry_es.entry)

    def test_delete_entry(self):
        self.user.is_superuser = True
        self.user.save()

        entry_id = self.vocab_entry_es.id

        self.assertTrue(VocabEntry.objects.filter(id=entry_id).exists())

        self.browser.get(
            "{0}{1}".format(
                self.live_server_url,
                reverse(
                    "vocab:vocab_entry_update",
                    kwargs={
                        "vocab_entry_language": self.vocab_entry_es.language,
                        "vocab_entry_slug": self.vocab_entry_es.slug
                    }
                )
            )
        )
        self.login_user(self.user.username)
        self.load_page(page_titles["vocab_entry_update_en"])
        self.open_modal(
            trigger_id="vocab-entry-delete-trigger",
            modal_id="delete-entry-modal"
        )
        self.get_element_by_id("vocab-entry-delete-ok").click()
        self.load_page(page_titles["vocab_entries_en"])

        self.assertFalse(VocabEntry.objects.filter(id=entry_id).exists())


# class VocabEntryAuthTest(TestCommon):

#     def setUp(self):
#         super(VocabEntryAuthTest, self).setUp()
#         self.vocab_entry_es = VocabEntry.objects.create(
#             language="es",
#             entry="tergiversar"
#         )

#     def test_create_entry(self):
#         self.browser.get("{0}{1}".format(
#             self.live_server_url,
#             reverse("vocab:vocab_user_dashboard"))
#         )
#         self.login_user(self.user.username)
#         self.load_page(page_titles["vocab_user_dashboard_en"])
#         self.open_sidebar()
#         self.open_modal(
#             trigger_id="sidebar-nav-vocab-entry-create",
#             modal_id="create-entry-modal"
#         )

#     def test_entries(self):
#         self.browser.get("{0}{1}".format(
#             self.live_server_url,
#             reverse("vocab:vocab_entries"))
#         )
#         self.login_user(self.user.username)
#         self.load_page(page_titles["vocab_entries_en"])
#         search_language = "es"
#         self.search_autocomplete_by_language(search_language, self.vocab_entry_es.entry)

#     def test_delete_entry(self):
#         self.user.is_superuser = True
#         self.user.save()

#         entry_id = self.vocab_entry_es.id

#         self.assertTrue(VocabEntry.objects.filter(id=entry_id).exists())

#         self.browser.get(
#             "{0}{1}".format(
#                 self.live_server_url,
#                 reverse(
#                     "vocab:vocab_entry_update",
#                     kwargs={
#                         "vocab_entry_language": self.vocab_entry_es.language,
#                         "vocab_entry_slug": self.vocab_entry_es.slug
#                     }
#                 )
#             )
#         )
#         self.login_user(self.user.username)
#         self.load_page(page_titles["vocab_entry_update_en"])
#         self.open_modal(
#             trigger_id="vocab-entry-delete-trigger",
#             modal_id="delete-entry-modal"
#         )
#         self.get_element_by_id("vocab-entry-delete-ok").click()
#         self.load_page(page_titles["vocab_entries_en"])

#         self.assertFalse(VocabEntry.objects.filter(id=entry_id).exists())


class VocabContextAuthTest(TestCommon):

    def setUp(self):
        super(VocabContextAuthTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.CREATED,
            name="Una prueba"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="He likes to eat pizza on Sunday. She likes to eat pizza on Friday."
        )
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="pizza"
        )

    def get_tag_xpath(self, tagbox_id=None, tag=None, close=False):
        if tagbox_id and tag:
            if not close:
                xpath = "//a[contains(., '{0}') and ancestor::div[@id='{1}']]".format(
                    tag,
                    tagbox_id
                )
            else:
                # Get tag"s close button xpath.
                xpath = "//a[@class='delete-tag' and preceding-sibling::a[contains(., '{0}')] and ancestor::div[@id='{1}']]".format(
                    tag,
                    tagbox_id
                )
            return xpath

    def add_tag(self, tagbox_id=None, tag=None, return_key=False):
        if tagbox_id and tag:
            css_selector = "#{0} .autocomplete-input".format(tagbox_id)
            tagbox_input = self.get_element_by_css(css_selector)
            tagbox_input.send_keys(tag)
        if return_key:
            tagbox_input.send_keys(u"\ue007")

    def get_highlight_xpath(self, tag):
        xpath = "//mark[@class='tagged-text' and contains(., '{0}')]".format(tag)
        return xpath

    def tag_hover(self, tag_element):
        hover = ActionChains(self.browser).move_to_element(tag_element)
        hover.perform()

    def test_tag_context(self):
        vocab_entry_tagbox_id = "vocab-entry-tags"
        vocab_entry_instance_tagbox_id = "vocab-entry-instance-tagbox"
        vocab_entry_instance_container_id = "vocab-entry-instance-tags"

        self.browser.get("{0}{1}".format(
            self.live_server_url,
            reverse(
                "vocab:vocab_context_tag",
                kwargs={"vocab_context_pk": self.vocab_context.id}
            )
        ))
        self.login_user(self.user.username)
        self.load_page(page_titles["vocab_context_tag_en"])

        # Context entry doesn"t exist yet.
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context,
                vocab_entry_id=self.vocab_entry
            ).exists()
        )

        # Search and select entry through autocompilete.
        link = self.search_autocomplete_by_language(
            self.vocab_entry.language,
            self.vocab_entry.entry
        )
        link.click()

        # Load tag in vocab entry tagbox and select it.
        vocab_entry_xp = self.get_tag_xpath(tagbox_id=vocab_entry_tagbox_id, tag=self.vocab_entry.entry)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, vocab_entry_xp)))
        self.get_element_by_xpath(vocab_entry_xp).click()

        # Vocab entry instance tagbox appears.
        self.wait.until(EC.element_to_be_clickable((By.ID, vocab_entry_instance_tagbox_id)))

        # Context entry now exists.
        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context,
                vocab_entry_id=self.vocab_entry
            ).exists()
        )
        vocab_context_entry = VocabContextEntry.objects.get(
            vocab_context_id=self.vocab_context,
            vocab_entry_id=self.vocab_entry
        )
        self.assertEqual(list(vocab_context_entry.get_vocab_entry_tags()), [])

        # Add tag to vocab context entry.
        self.add_tag(
            tagbox_id=vocab_entry_instance_tagbox_id,
            tag=self.vocab_entry.entry,
            return_key=True
        )
        vocab_entry_instance_xp = self.get_tag_xpath(
            tagbox_id=vocab_entry_instance_container_id,
            tag=self.vocab_entry.entry
        )
        self.wait.until(EC.element_to_be_clickable((By.XPATH, vocab_entry_instance_xp)))
        vocab_entry_instance_tag = self.get_element_by_xpath(vocab_entry_instance_xp)

        # Vocab entry tags have been saved to VocabContextEntry object.
        self.assertEqual(list(vocab_context_entry.get_vocab_entry_tags()), [self.vocab_entry.entry])

        # Vocab entry instance is highlighted in text.
        vocab_entry_highlight_xp = self.get_highlight_xpath(tag=self.vocab_entry.entry)
        vocab_entry_highlighted = self.get_elements_by_xpath(vocab_entry_highlight_xp)
        self.assertEqual(len(vocab_entry_highlighted), 2)

        # Delete vocab instance tag.
        self.tag_hover(tag_element=vocab_entry_instance_tag)
        vocab_entry_instance_close_xp = self.get_tag_xpath(
            tagbox_id=vocab_entry_instance_container_id,
            tag=self.vocab_entry.entry,
            close=True
        )
        self.wait.until(EC.element_to_be_clickable((By.XPATH, vocab_entry_instance_close_xp)))
        self.get_element_by_xpath(vocab_entry_instance_close_xp).click()
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, vocab_entry_instance_xp)))
        self.assertEqual(list(vocab_context_entry.get_vocab_entry_tags()), [])

        # Delete vocab entry tag
        vocab_entry_tag = self.get_element_by_xpath(vocab_entry_xp)
        self.tag_hover(vocab_entry_tag)
        vocab_entry_close_xp = self.get_tag_xpath(
            tagbox_id=vocab_entry_tagbox_id,
            tag=self.vocab_entry.entry,
            close=True
        )
        self.wait.until(EC.element_to_be_clickable((By.XPATH, vocab_entry_close_xp)))
        self.get_element_by_xpath(vocab_entry_close_xp).click()
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, vocab_entry_xp)))

        # Context entry no longer exists.
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context,
                vocab_entry_id=self.vocab_entry
            ).exists()
        )
