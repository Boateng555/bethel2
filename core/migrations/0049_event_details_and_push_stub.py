from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0048_alter_globalsettings_footer_copyright"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="details",
            field=models.TextField(
                blank=True,
                help_text="Full event details (shown in the Event Details section). If empty, the short description is used.",
            ),
        ),
    ]

