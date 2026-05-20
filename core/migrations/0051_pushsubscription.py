# Generated manually for Web Push subscriptions

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0050_eventscheduleitem_second_speaker"),
    ]

    operations = [
        migrations.CreateModel(
            name="PushSubscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("endpoint", models.TextField(unique=True)),
                ("p256dh_key", models.TextField()),
                ("auth_key", models.TextField()),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("notify_events", models.BooleanField(default=True)),
                ("notify_news", models.BooleanField(default=True)),
                ("notify_sermons", models.BooleanField(default=True)),
                ("notify_live", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "church",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="push_subscriptions",
                        to="core.church",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="pushsubscription",
            index=models.Index(fields=["church", "is_active"], name="core_pushsu_church__a8f2c1_idx"),
        ),
    ]
