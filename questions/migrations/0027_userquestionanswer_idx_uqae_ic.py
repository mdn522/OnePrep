# Generated by Django 5.1.1 on 2024-10-19 19:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0020_exam_module_alter_exam_uuid'),
        ('questions', '0026_userquestionanswer_idx_uqae_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userquestionanswer',
            index=models.Index(fields=['user', 'question', 'exam', 'is_correct'], name='idx_uqae_ic'),
        ),
    ]
