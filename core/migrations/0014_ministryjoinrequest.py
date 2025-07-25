# Generated by Django 5.1.3 on 2025-06-30 23:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_localaboutpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinistryJoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_reviewed', models.BooleanField(default=False)),
                ('church', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.church')),
                ('ministry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='core.ministry')),
            ],
            options={
                'verbose_name': 'Ministry Join Request',
                'verbose_name_plural': 'Ministry Join Requests',
                'ordering': ['-created_at'],
            },
        ),
    ]
