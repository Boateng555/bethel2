from django.db.models.signals import post_save, pre_save
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


def _connect_push_notifications():
    from django.apps import apps

    Event = apps.get_model('core', 'Event')
    News = apps.get_model('core', 'News')
    Sermon = apps.get_model('core', 'Sermon')

    def on_event_saved(sender, instance, created, **kwargs):
        if created:
            from .push_notifications import notify_new_event
            notify_new_event(instance)

    def on_news_saved(sender, instance, created, **kwargs):
        if created:
            from .push_notifications import notify_new_news
            notify_new_news(instance)

    def on_sermon_saved(sender, instance, created, **kwargs):
        if created:
            from .push_notifications import notify_new_sermon
            notify_new_sermon(instance)

    post_save.connect(on_event_saved, sender=Event, dispatch_uid='push_notify_event')
    post_save.connect(on_news_saved, sender=News, dispatch_uid='push_notify_news')
    post_save.connect(on_sermon_saved, sender=Sermon, dispatch_uid='push_notify_sermon')


def connect_signals():
    _connect_media_compression()
    _connect_push_notifications()
