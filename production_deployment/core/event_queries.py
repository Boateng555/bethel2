"""Shared queryset helpers for public event listings."""
from datetime import timedelta

from django.utils import timezone

# Keep events on home page "Upcoming Events" for this long after they end
UPCOMING_EVENT_GRACE_DAYS = 7


def upcoming_events_cutoff():
    """Events with end_date on or after this moment are still shown as upcoming."""
    return timezone.now() - timedelta(days=UPCOMING_EVENT_GRACE_DAYS)
