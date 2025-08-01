# Generated by Django 5.1.3 on 2025-07-09 14:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_heromedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='heromedia',
            name='church',
            field=models.ForeignKey(blank=True, help_text='(Optional) Direct link to church for admin inline. Leave blank to use only via Hero.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hero_media', to='core.church'),
        ),
    ]
