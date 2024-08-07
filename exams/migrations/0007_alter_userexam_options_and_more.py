# Generated by Django 5.0.6 on 2024-06-19 01:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0006_exam_prevent_copy_exam_retake_exam_retake_after_and_more'),
        ('questions', '0008_userquestionstatus_saw_explanation_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userexam',
            options={'verbose_name': 'User Exam'},
        ),
        migrations.RemoveIndex(
            model_name='userexam',
            name='exams_usere_user_id_3a269e_idx',
        ),
        migrations.RemoveIndex(
            model_name='userexam',
            name='exams_usere_exam_id_0882bf_idx',
        ),
        migrations.AddField(
            model_name='examquestion',
            name='can_see_explanation',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='examquestion',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_question_set', to='exams.exam'),
        ),
        migrations.AlterField(
            model_name='examquestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_question_set', to='questions.question'),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_exam_set', to='exams.exam'),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_exam_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
