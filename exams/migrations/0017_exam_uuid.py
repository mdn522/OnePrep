# Generated by Django 5.0.6 on 2024-09-16 08:34

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0016_remove_exam_unique_exam_source_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='uuid',
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
    ]
