import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .models import Church, PushSubscription
from .push_notifications import webpush_enabled
from .pwa_utils import public_static_url


@require_GET
def push_notifications_js(request):
    """Serve push-notifications.js via Django so Enable works even if /static/ is misconfigured."""
    js_path = Path(settings.BASE_DIR) / 'static' / 'js' / 'push-notifications.js'
    try:
        content = js_path.read_text(encoding='utf-8')
    except OSError:
        return HttpResponse('// push-notifications.js not found', status=404, content_type='application/javascript')
    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=300'
    return response


@require_GET
def push_vapid_public_key(request):
    key = getattr(settings, 'WEBPUSH_VAPID_PUBLIC_KEY', '')
    return JsonResponse({'publicKey': key, 'enabled': webpush_enabled()})


@require_POST
@csrf_protect
def push_subscribe(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    endpoint = data.get('endpoint', '').strip()
    keys = data.get('keys') or {}
    p256dh = keys.get('p256dh', '').strip()
    auth = keys.get('auth', '').strip()
    church_id = data.get('church_id')

    if not endpoint or not p256dh or not auth:
        return JsonResponse({'error': 'Missing subscription data'}, status=400)
    if not church_id:
        return JsonResponse({'error': 'church_id is required'}, status=400)

    try:
        church = Church.objects.get(pk=church_id)
    except (Church.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Church not found'}, status=404)

    ua = request.META.get('HTTP_USER_AGENT', '')[:500]
    sub, created = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'church': church,
            'p256dh_key': p256dh,
            'auth_key': auth,
            'user_agent': ua,
            'is_active': True,
            'notify_events': data.get('notify_events', True),
            'notify_news': data.get('notify_news', True),
            'notify_sermons': data.get('notify_sermons', True),
            'notify_live': data.get('notify_live', True),
        },
    )
    return JsonResponse({'ok': True, 'created': created, 'id': str(sub.id)})


@require_POST
@csrf_protect
def push_unsubscribe(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    endpoint = data.get('endpoint', '').strip()
    if not endpoint:
        return JsonResponse({'error': 'Missing endpoint'}, status=400)

    updated = PushSubscription.objects.filter(endpoint=endpoint).update(is_active=False)
    return JsonResponse({'ok': True, 'updated': updated})


def service_worker_js(request):
    """Serve service worker from site root scope."""
    content = """/* Bethel Web Push Service Worker */
self.addEventListener('push', function(event) {
  if (!event.data) return;
  var data = {};
  try {
    data = event.data.json();
  } catch (e) {
    data = { title: 'Bethel', body: event.data.text() };
  }
  var title = data.title || 'Bethel Prayer Ministry';
  var options = {
    body: data.body || '',
    icon: data.icon || '/static/img/bethel_logo.png',
    badge: '/static/img/bethel_logo.png',
    tag: data.tag || 'bethel',
    data: { url: data.url || '/' },
    requireInteraction: false,
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  var url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
"""
    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


def web_app_manifest(request):
    site_name = 'Bethel Prayer Ministry International'
    try:
        from .models import GlobalSettings
        gs = GlobalSettings.objects.first()
        if gs and gs.site_name:
            site_name = gs.site_name
    except Exception:
        pass

    start_url = request.GET.get('start', '/').strip()
    if not start_url.startswith('/'):
        start_url = '/'

    manifest = {
        'name': site_name,
        'short_name': 'Bethel',
        'description': 'Events, sermons, and news from your Bethel church',
        'start_url': start_url,
        'display': 'standalone',
        'background_color': '#1e3a8a',
        'theme_color': '#1e3a8a',
        'icons': [
            {
                'src': public_static_url('/static/img/icon-192.png', cache_bust=''),
                'sizes': '192x192',
                'type': 'image/png',
                'purpose': 'any',
            },
            {
                'src': public_static_url('/static/img/icon-512.png', cache_bust=''),
                'sizes': '512x512',
                'type': 'image/png',
                'purpose': 'any',
            },
            {
                'src': public_static_url('/static/img/apple-touch-icon.png', cache_bust=''),
                'sizes': '180x180',
                'type': 'image/png',
                'purpose': 'any',
            },
        ],
    }
    return JsonResponse(manifest)


@require_GET
def apple_touch_icon(request):
    """iOS looks for /apple-touch-icon.png at the site root."""
    from pathlib import Path

    icon_path = Path(settings.BASE_DIR) / 'static' / 'img' / 'apple-touch-icon.png'
    try:
        data = icon_path.read_bytes()
    except OSError:
        return HttpResponse(status=404)
    response = HttpResponse(data, content_type='image/png')
    response['Cache-Control'] = 'public, max-age=86400'
    return response
