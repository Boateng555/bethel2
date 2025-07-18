# Generated by Django 5.1.3 on 2025-07-01 17:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_event_is_big_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSpeaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='events/speakers/')),
                ('title', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField(blank=True)),
                ('facebook', models.URLField(blank=True)),
                ('twitter', models.URLField(blank=True)),
                ('instagram', models.URLField(blank=True)),
                ('linkedin', models.URLField(blank=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='speakers', to='core.event')),
            ],
        ),
        migrations.CreateModel(
            name='EventScheduleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_items', to='core.event')),
                ('speaker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_items', to='core.eventspeaker')),
            ],
        ),
    ]
