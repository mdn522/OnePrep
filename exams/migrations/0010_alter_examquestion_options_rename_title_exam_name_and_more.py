# Generated by Django 5.0.6 on 2024-07-03 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0009_exam_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examquestion',
            options={'ordering': ['order'], 'verbose_name': 'Exam Question'},
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='title',
            new_name='name',
        ),
        migrations.AddField(
            model_name='exam',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
