# Generated by Django 5.0.6 on 2024-09-16 08:35

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0018_add_unique_exam_uuids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
