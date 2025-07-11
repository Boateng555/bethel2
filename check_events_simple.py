#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Event
from django.utils import timezone

# Get the church
church = Church.objects.get(name='bethel  kumasi')
print(f"Church: {church.name}")

# Get all events for this church
events = Event.objects.filter(church=church)
print(f"Total events: {events.count()}")

# Get public events
public_events = Event.objects.filter(church=church, is_public=True)
print(f"Public events: {public_events.count()}")

# Get future events
future_events = Event.objects.filter(church=church, is_public=True, start_date__gte=timezone.now())
print(f"Future public events for {church.name}: {future_events.count()}")

for e in future_events:
    print(f"- {e.title} on {e.start_date} (is_public: {e.is_public})") 