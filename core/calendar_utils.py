"""Build .ics calendar files for events."""
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Church events are in Germany — use local times in calendar apps
EVENT_TZ = ZoneInfo('Europe/Berlin')


def ics_escape(text: str) -> str:
    """Escape text per RFC 5545 for ICS property values."""
    if not text:
        return ''
    return (
        str(text)
        .replace('\\', '\\\\')
        .replace('\r\n', '\\n')
        .replace('\r', '\\n')
        .replace('\n', '\\n')
        .replace(',', '\\,')
        .replace(';', '\\;')
    )


def _aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _to_ics_local(dt) -> str:
    """Local Europe/Berlin time for DTSTART/DTEND (no UTC shift on phones)."""
    local = _aware(dt).astimezone(EVENT_TZ)
    return local.strftime('%Y%m%dT%H%M%S')


def _to_ics_utc_stamp(dt) -> str:
    return _aware(dt).astimezone(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%SZ')


def event_public_page_path(event) -> str:
    """Relative URL for the event detail page on this site."""
    if event.church_id:
        return reverse('church_event_detail', args=[event.church_id, event.id])
    return reverse('event_detail', args=[event.id])


def event_absolute_url(event, request=None) -> str:
    """
    Always use the canonical public domain so calendar URL links open the real site.
    (Avoid bethel-prayer-ministry-international.com which can show a blank page.)
    """
    path = event_public_page_path(event)
    domain = getattr(settings, 'CANONICAL_PUBLIC_DOMAIN', '').strip()
    if not domain:
        domain = 'bethelprayerministryinternational.com'
    return f'https://{domain.rstrip("/")}{path}'


def _calendar_end_datetime(event):
    """End time for .ics — fix admin mistakes that span many days for a single service."""
    start_dt = _aware(event.start_date)
    end_dt = _aware(event.end_date or event.start_date)
    if end_dt <= start_dt:
        return start_dt + timedelta(hours=2)

    span = end_dt - start_dt
    if event.is_big_event or event.event_type in ('convention', 'conference'):
        return end_dt
    if span > timedelta(days=1):
        return start_dt + timedelta(hours=2, minutes=30)
    return end_dt


def build_event_ics(event, request) -> str:
    """Return a complete VCALENDAR string with event URL and correct local times."""
    start_dt = _aware(event.start_date)
    end_dt = _calendar_end_datetime(event)

    event_url = event_absolute_url(event, request)
    now_stamp = _to_ics_utc_stamp(timezone.now())
    start = _to_ics_local(start_dt)
    end = _to_ics_local(end_dt)

    body = (event.details or event.description or '').strip()
    desc_parts = []
    if body:
        desc_parts.append(body)
    desc_parts.append(f'Event page: {event_url}')
    description = ics_escape('\n\n'.join(desc_parts))

    location_parts = []
    if event.location:
        location_parts.append(event.location.strip())
    if event.address and event.address.strip():
        location_parts.append(event.address.strip())
    location = ics_escape(', '.join(location_parts))

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Bethel Prayer Ministry//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        f'UID:{event.id}@bethelprayerministryinternational.com',
        f'DTSTAMP:{now_stamp}',
        f'DTSTART;TZID=Europe/Berlin:{start}',
        f'DTEND;TZID=Europe/Berlin:{end}',
        f'SUMMARY:{ics_escape(event.title)}',
        f'DESCRIPTION:{description}',
        f'URL:{event_url}',
        'STATUS:CONFIRMED',
    ]
    if location:
        lines.append(f'LOCATION:{location}')
    lines.extend(['END:VEVENT', 'END:VCALENDAR'])
    return '\r\n'.join(lines) + '\r\n'
