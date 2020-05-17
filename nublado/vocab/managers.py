from django.db import models
from django.db.models.functions import Lower
from django.db.models import Count

from core.managers import OrderedModelManager


class VocabEntryManager(models.Manager):
    pass


class VocabSourceManager(models.Manager):
    pass


class VocabContextManager(OrderedModelManager):

    def get_queryset(self):
        return super(VocabContextManager, self).get_queryset().select_related("vocab_source")


class VocabContextEntryManager(models.Manager):

    def source_entry_language_freq(self, vocab_source_id):
        qs = super().get_queryset()
        qs = qs.select_related("vocab_context", "vocab_entry")
        qs = qs.filter(vocab_context__vocab_source_id=vocab_source_id)
        qs = qs.values(language=Lower("vocab_entry__language"))
        qs = qs.annotate(freq=Count("vocab_entry_id", distinct=True))

        return qs

    def source_entry_language_max(self, vocab_source_id):
        """
        Returns the vocab entry language with the greatest frequency in the source.
        """

        qs = self.source_entry_language_freq(vocab_source_id).order_by("-freq")

        if qs:
            return qs[0]["language"]
        else:
            return None
