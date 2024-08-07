# Generated by Django 5.0.6 on 2024-06-12 09:51

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('source', models.CharField(blank=True, max_length=24, null=True)),
                ('source_order', models.PositiveIntegerField()),
                ('source_id', models.CharField(max_length=64, null=True)),
                ('source_id_2', models.CharField(max_length=64, null=True)),
                ('source_id_3', models.CharField(max_length=64, null=True)),
                ('source_raw_data', models.JSONField(default=None)),
                ('module', models.CharField(choices=[('en', 'English'), ('math', 'Math')], max_length=4)),
                ('stimulus', models.TextField(default='')),
                ('stem', models.TextField(default='')),
                ('difficulty', models.IntegerField(choices=[(0, 'Unspecified'), (1, 'Easy'), (2, 'Medium'), (3, 'Hard')])),
                ('answer_type', models.CharField(choices=[('mcq', 'Multiple Choice'), ('spr', 'SPR')], default='', max_length=24)),
                ('explanation', models.TextField(default='')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.program')),
            ],
        ),
        migrations.CreateModel(
            name='AnswerChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('text', models.TextField()),
                ('explanation', models.TextField(blank=True, default='')),
                ('correct', models.BooleanField(default=False)),
                ('order', models.PositiveSmallIntegerField()),
                ('letter', models.CharField(max_length=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question')),
            ],
            options={
                'verbose_name': 'Answer Choice',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('value', models.CharField(max_length=24, null=True)),
                ('explanation', models.TextField(blank=True, default='')),
                ('order', models.PositiveSmallIntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), ('source_id__isnull', False)), fields=('source', 'source_id'), name='unique_question_source_id'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), ('source_id_2__isnull', False)), fields=('source', 'source_id_2'), name='unique_question_source_id_2'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), ('source_id_3__isnull', False)), fields=('source', 'source_id_3'), name='unique_question_source_id_3'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.Index(condition=models.Q(('source__isnull', False)), fields=['source'], name='index_question_source'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.Index(condition=models.Q(('source__isnull', False), ('source_id__isnull', False)), fields=['source', 'source_id'], name='index_question_source_id'),
        ),
        migrations.AddConstraint(
            model_name='answerchoice',
            constraint=models.UniqueConstraint(condition=models.Q(('correct', True)), fields=('question', 'correct'), name='unique_question_answer_choice_correct'),
        ),
        migrations.AddConstraint(
            model_name='answerchoice',
            constraint=models.UniqueConstraint(fields=('question', 'order'), name='unique_question_answer_choice_order'),
        ),
        migrations.AddConstraint(
            model_name='answerchoice',
            constraint=models.UniqueConstraint(fields=('question', 'letter'), name='unique_question_answer_choice_letter'),
        ),
    ]
