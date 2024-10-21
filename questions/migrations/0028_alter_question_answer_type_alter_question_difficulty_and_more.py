# Generated by Django 5.1.1 on 2024-10-19 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0027_userquestionanswer_idx_uqae_ic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('mcq', 'Multiple Choice'), ('spr', 'SPR')], db_index=True, default='', max_length=24),
        ),
        migrations.AlterField(
            model_name='question',
            name='difficulty',
            field=models.CharField(blank=True, choices=[('', 'Unspecified'), ('E', 'Easy'), ('M', 'Medium'), ('H', 'Hard')], db_index=True, default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='question',
            name='module',
            field=models.CharField(choices=[('en', 'English'), ('math', 'Math')], db_index=True, max_length=4),
        ),
    ]