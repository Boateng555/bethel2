# Generated by Django 5.1.3 on 2025-06-30 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_testimony'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='About Us', max_length=200)),
                ('intro', models.TextField(blank=True, verbose_name='Intro/Mission')),
                ('founding_story', models.TextField(blank=True, verbose_name='Founding Story')),
                ('timeline', models.TextField(blank=True, verbose_name='Timeline')),
                ('leadership_timeline', models.TextField(blank=True, verbose_name='Leadership Timeline')),
                ('ministry_today', models.TextField(blank=True, verbose_name='Ministry Today')),
                ('quick_facts', models.TextField(blank=True, verbose_name='Quick Facts')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('founder_image', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('extra_image', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'About Page',
                'verbose_name_plural': 'About Page',
            },
        ),
    ]
