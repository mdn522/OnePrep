# Generated by Django 5.1.1 on 2024-10-03 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_profile_has_donated_profile_last_donated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_donation_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Last Donation Amount'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_donation_currency',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='Last Donation Currency'),
        ),
    ]
