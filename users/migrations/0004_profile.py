# Generated by Django 5.1.1 on 2024-10-03 05:14

import django.db.models.deletion
import timezone_field.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timezone', timezone_field.fields.TimeZoneField(blank=True, choices_display='WITH_GMT_OFFSET', default='UTC')),
                ('theme', models.CharField(default='light', max_length=255)),
                ('notes', models.TextField(blank=True, default='')),
                ('bio', models.TextField(blank=True, default='', max_length=240)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
