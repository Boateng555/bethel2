# Generated by Django 5.1.3 on 2025-06-28 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationmethod',
            name='external_link',
            field=models.URLField(blank=True, help_text='Direct link to PayPal, GoFundMe, etc.', null=True),
        ),
        migrations.AlterField(
            model_name='donationmethod',
            name='account_info',
            field=models.TextField(help_text='Account details, email, or payment instructions (if no external link)'),
        ),
    ]
