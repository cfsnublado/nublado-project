from django.db.models.signals import post_init
from django.dispatch import receiver

from .models import VocabEntry


@receiver(post_init, sender=VocabEntry)
def vocab_entry_post_init_handler(sender, instance, **kwargs):
    if instance.pk:
        instance.init_tracked_fields()
