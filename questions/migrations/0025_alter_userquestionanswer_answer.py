# Generated by Django 5.1.1 on 2024-10-16 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0024_alter_question_difficulty_alter_question_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquestionanswer',
            name='answer',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
