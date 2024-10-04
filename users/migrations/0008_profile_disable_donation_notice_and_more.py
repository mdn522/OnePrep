# Generated by Django 5.1.1 on 2024-10-04 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_profile_last_donation_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='disable_donation_notice',
            field=models.BooleanField(blank=True, default=False, verbose_name='Disable Donation Notice'),
        ),
        migrations.AddField(
            model_name='profile',
            name='disable_donation_notice_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Disable Donation Notice Until'),
        ),
    ]
