from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0049_event_details_and_push_stub"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventscheduleitem",
            name="speaker_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="schedule_items_secondary",
                to="core.eventspeaker",
            ),
        ),
    ]

