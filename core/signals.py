from django.db.models.signals import pre_save
from django.dispatch import receiver

from .media_utils import compress_model_media

HERO_MEDIA_MODELS = ('EventHeroMedia', 'HeroMedia')
IMAGE_MODELS = (
    'EventSpeaker', 'EventHighlight', 'Ministry', 'News', 'Sermon',
    'Church', 'Hero', 'Convention', 'LocalAboutPage', 'LocalLeadershipPage',
)


def _connect_media_compression():
    from django.apps import apps
    for label in HERO_MEDIA_MODELS + IMAGE_MODELS:
        try:
            model = apps.get_model('core', label)
        except LookupError:
            continue

        def make_handler(is_hero):
            def handler(sender, instance, **kwargs):
                compress_model_media(instance, hero=is_hero)
            return handler

        pre_save.connect(
            make_handler(label in HERO_MEDIA_MODELS),
            sender=model,
            dispatch_uid=f'compress_media_{label}',
        )


def connect_signals():
    _connect_media_compression()
