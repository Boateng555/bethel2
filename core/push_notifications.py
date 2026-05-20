"""Web Push notification delivery for Bethel sites."""
import json
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def webpush_enabled():
    return bool(
        getattr(settings, 'WEBPUSH_VAPID_PUBLIC_KEY', '')
        and getattr(settings, 'WEBPUSH_VAPID_PRIVATE_KEY', '')
    )


def get_vapid_claims():
    email = getattr(settings, 'WEBPUSH_VAPID_ADMIN_EMAIL', 'admin@bethelprayerministryinternational.com')
    if not email.startswith('mailto:'):
        email = f'mailto:{email}'
    return {'sub': email}


def build_absolute_url(path, request=None):
    if path.startswith('http'):
        return path
    site_domain = getattr(settings, 'SITE_DOMAIN', '').strip()
    if site_domain:
        scheme = 'https'
        return f'{scheme}://{site_domain}{path}'
    if request:
        return request.build_absolute_uri(path)
    return path


def send_web_push(subscription, payload, ttl=86400):
    """Send one push message. Returns True on success."""
    if not webpush_enabled():
        return False
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning('pywebpush not installed; skipping push')
        return False

    vapid_claims = get_vapid_claims()
    subscription_info = {
        'endpoint': subscription.endpoint,
        'keys': {
            'p256dh': subscription.p256dh_key,
            'auth': subscription.auth_key,
        },
    }
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
            vapid_claims=vapid_claims,
            ttl=ttl,
        )
        return True
    except Exception as exc:
        exc_name = type(exc).__name__
        if exc_name == 'WebPushException':
            status = getattr(exc, 'response', None)
            status_code = getattr(status, 'status_code', None) if status else None
            if status_code in (404, 410):
                subscription.is_active = False
                subscription.save(update_fields=['is_active', 'updated_at'])
            logger.info('Web push failed (%s) for %s', status_code, subscription.endpoint[:48])
        else:
            logger.warning('Web push error: %s', exc)
        return False


def notify_church_subscribers(
    church,
    *,
    title,
    body,
    url_path,
    tag='bethel-update',
    notification_type='general',
    request=None,
):
    """Send push to all active subscriptions for a church."""
    if not webpush_enabled():
        return 0

    from .models import PushSubscription

    field_map = {
        'event': 'notify_events',
        'news': 'notify_news',
        'sermon': 'notify_sermons',
        'live': 'notify_live',
    }
    pref_field = field_map.get(notification_type)
    qs = PushSubscription.objects.filter(is_active=True, church=church)
    if pref_field:
        qs = qs.filter(**{pref_field: True})

    url = build_absolute_url(url_path, request=request)
    payload = {
        'title': title,
        'body': body,
        'url': url,
        'tag': tag,
        'icon': build_absolute_url('/static/img/bethel_logo.png', request=request),
    }

    sent = 0
    for sub in qs.iterator():
        if send_web_push(sub, payload):
            sent += 1
    return sent


def notify_new_event(event, request=None):
    if not event.is_public:
        return 0
    church = event.church
    path = reverse(
        'church_event_detail',
        kwargs={'church_id': church.id, 'event_id': event.id},
    )
    date_str = event.start_date.strftime('%b %d, %Y') if event.start_date else ''
    body = event.description[:120] + ('…' if len(event.description) > 120 else '')
    if date_str:
        body = f'{date_str} — {body}'
    return notify_church_subscribers(
        church,
        title=f'New event: {event.title}',
        body=body,
        url_path=path,
        tag=f'event-{event.id}',
        notification_type='event',
        request=request,
    )


def notify_new_news(article, request=None):
    if not article.is_public:
        return 0
    church = article.church
    path = reverse('news_detail', kwargs={'news_id': article.id})
    excerpt = (article.excerpt or article.content)[:120]
    return notify_church_subscribers(
        church,
        title=f'News: {article.title}',
        body=excerpt + ('…' if len(excerpt) >= 120 else ''),
        url_path=path,
        tag=f'news-{article.id}',
        notification_type='news',
        request=request,
    )


def notify_new_sermon(sermon, request=None):
    church = sermon.church
    path = reverse('church_sermons', kwargs={'church_id': church.id})
    body = f'{sermon.preacher} — {sermon.description[:80]}'
    return notify_church_subscribers(
        church,
        title=f'New sermon: {sermon.title}',
        body=body,
        url_path=path,
        tag=f'sermon-{sermon.id}',
        notification_type='sermon',
        request=request,
    )
