#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Event

print("=== CHURCHES ===")
churches = Church.objects.all()
for church in churches:
    print(f"- {church.name} (ID: {church.id})")
    events = Event.objects.filter(church=church)
    print(f"  Events: {events.count()}")
    for event in events:
        print(f"    - {event.title} on {event.start_date}")

print("\n=== ALL EVENTS ===")
all_events = Event.objects.all()
print(f"Total events: {all_events.count()}")
for event in all_events:
    print(f"- {event.title} for {event.church.name} on {event.start_date}") 