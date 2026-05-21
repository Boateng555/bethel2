"""Build .ics calendar files for events."""
from datetime import datetime, timezone as dt_timezone

from django.urls import reverse
from django.utils import timezone


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


def _to_ics_utc(dt) -> str:
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt.astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def event_public_page_path(event) -> str:
    """Relative URL for the event detail page on this site."""
    if event.church_id:
        return reverse('church_event_detail', args=[event.church_id, event.id])
    return reverse('event_detail', args=[event.id])


def build_event_ics(event, request) -> str:
    """Return a complete VCALENDAR string with event URL and correct times."""
    start_dt = event.start_date
    end_dt = event.end_date or event.start_date
    if end_dt < start_dt:
        end_dt = start_dt

    event_url = request.build_absolute_uri(event_public_page_path(event))
    now_stamp = _to_ics_utc(timezone.now())
    start = _to_ics_utc(start_dt)
    end = _to_ics_utc(end_dt)

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
        f'DTSTART:{start}',
        f'DTEND:{end}',
        f'SUMMARY:{ics_escape(event.title)}',
        f'DESCRIPTION:{description}',
        f'URL:{event_url}',
    ]
    if location:
        lines.append(f'LOCATION:{location}')
    lines.extend(['END:VEVENT', 'END:VCALENDAR'])
    return '\r\n'.join(lines) + '\r\n'
