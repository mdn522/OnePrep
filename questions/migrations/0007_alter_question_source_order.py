# Generated by Django 5.0.6 on 2024-06-15 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_alter_question_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='source_order',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
