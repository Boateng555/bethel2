# Generated by Django 5.1.3 on 2025-07-06 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_delete_conventionregistration'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventHeroMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='hero/')),
                ('video', models.FileField(blank=True, null=True, upload_to='hero/videos/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hero_media', to='core.event')),
            ],
        ),
    ]
