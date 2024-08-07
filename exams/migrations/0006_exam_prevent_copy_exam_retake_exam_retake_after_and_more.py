# Generated by Django 5.0.6 on 2024-06-15 03:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_exam_skill_tags_alter_examquestion_exam_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='prevent_copy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='retake',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='retake_after',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='UserExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('time_taken', models.DurationField(blank=True, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.exam')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Exam',
                'verbose_name_plural': 'User Exams',
                'indexes': [models.Index(fields=['user'], name='exams_usere_user_id_3a269e_idx'), models.Index(fields=['exam'], name='exams_usere_exam_id_0882bf_idx')],
            },
        ),
    ]
