# Generated by Django 5.1.3 on 2025-07-31 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_globalsettings_local_church_redirect_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='church',
            name='friday_service',
            field=models.TimeField(blank=True, help_text='Friday service time (optional)', null=True),
        ),
        migrations.AddField(
            model_name='church',
            name='other_services',
            field=models.TextField(blank=True, help_text="Other service times (e.g., 'Youth Service: Saturday 6:00 PM')"),
        ),
        migrations.AddField(
            model_name='church',
            name='service_times',
            field=models.TextField(blank=True, help_text="Enter service times (e.g., 'Sunday 9:00 AM & 11:00 AM', 'Wednesday 7:00 PM')"),
        ),
        migrations.AddField(
            model_name='church',
            name='sunday_service_1',
            field=models.TimeField(blank=True, help_text='First Sunday service time', null=True),
        ),
        migrations.AddField(
            model_name='church',
            name='sunday_service_2',
            field=models.TimeField(blank=True, help_text='Second Sunday service time (optional)', null=True),
        ),
        migrations.AddField(
            model_name='church',
            name='wednesday_service',
            field=models.TimeField(blank=True, help_text='Wednesday service time (optional)', null=True),
        ),
    ]
