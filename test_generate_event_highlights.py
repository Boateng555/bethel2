import pytest
from django.utils import timezone
from django.core.management import call_command
from core.models import Event, EventHighlight, Church

@pytest.mark.django_db
def test_generate_event_highlights_creates_highlights_for_past_events():
    # Setup: create a church and two past events, one with a highlight, one without
    church = Church.objects.create(name="Test Church", address="123 Main St", city="Testville", country="Testland")
    now = timezone.now()
    event1 = Event.objects.create(
        church=church,
        title="Past Event 1",
        description="Description 1",
        start_date=now.replace(year=now.year-1),
        end_date=now.replace(year=now.year-1, hour=now.hour+2),
        is_public=True
    )
    event2 = Event.objects.create(
        church=church,
        title="Past Event 2",
        description="Description 2",
        start_date=now.replace(year=now.year-2),
        end_date=now.replace(year=now.year-2, hour=now.hour+2),
        is_public=True
    )
    # Only event1 has a highlight initially
    EventHighlight.objects.create(
        event=event1,
        church=church,
        title=event1.title,
        description=event1.description,
        year=event1.start_date.year,
        is_public=True
    )
    # Run the management command
    call_command('generate_event_highlights')
    # Assert: event1 still has one highlight, event2 now has one
    assert EventHighlight.objects.filter(event=event1).count() == 1
    assert EventHighlight.objects.filter(event=event2).count() == 1
    # The highlight for event2 should have correct fields
    highlight2 = EventHighlight.objects.get(event=event2)
    assert highlight2.title == event2.title
    assert highlight2.description == event2.description
    assert highlight2.year == event2.start_date.year
    assert highlight2.is_public is True 