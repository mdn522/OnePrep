# Generated by Django 5.1.1 on 2024-10-19 19:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0020_exam_module_alter_exam_uuid'),
        ('questions', '0025_alter_userquestionanswer_answer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userquestionanswer',
            index=models.Index(fields=['user', 'question', 'exam'], name='idx_uqae'),
        ),
        migrations.AddIndex(
            model_name='userquestionstatus',
            index=models.Index(fields=['user', 'question', 'is_marked_for_review'], name='idx_uqse_mfr'),
        ),
    ]