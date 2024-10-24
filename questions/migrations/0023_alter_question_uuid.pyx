# Generated by Django 5.1.1 on 2024-09-22 11:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0022_auto_20240916_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID'),
        ),
    ]
