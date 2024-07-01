# Generated by Django 5.0.6 on 2024-06-30 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0009_alter_question_difficulty'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='answerchoice',
            name='unique_question_answer_choice_correct',
        ),
        migrations.RenameField(
            model_name='answerchoice',
            old_name='correct',
            new_name='is_correct',
        ),
        migrations.AddField(
            model_name='userquestionanswer',
            name='answer_choice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.answerchoice'),
        ),
        migrations.AddField(
            model_name='userquestionanswer',
            name='answer_group_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='userquestionanswer',
            name='saw_explanation_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userquestionanswer',
            name='saw_explanation_before',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='userquestionstatus',
            name='is_skipped',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='userquestionstatus',
            name='marked_for_review_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userquestionanswer',
            name='answer',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='userquestionanswer',
            name='time_taken',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name='answerchoice',
            constraint=models.UniqueConstraint(condition=models.Q(('is_correct', True)), fields=('question', 'is_correct'), name='unique_question_answer_choice_correct'),
        ),
    ]
