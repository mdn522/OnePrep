# Generated by Django 5.0.6 on 2024-09-01 18:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('programs', '0001_initial'),
        ('questions', '0018_alter_question_skill_tags'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='question',
            name='unique_question_source_id',
        ),
        migrations.RemoveConstraint(
            model_name='question',
            name='unique_question_source_id_2',
        ),
        migrations.RemoveConstraint(
            model_name='question',
            name='unique_question_source_id_3',
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), models.Q(('source', ''), _negated=True), ('source_id__isnull', False), models.Q(('source_id', ''), _negated=True)), fields=('source', 'source_id'), name='unique_question_source_id'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), models.Q(('source', ''), _negated=True), ('source_id_2__isnull', False), models.Q(('source_id_2', ''), _negated=True)), fields=('source', 'source_id_2'), name='unique_question_source_id_2'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(condition=models.Q(('source__isnull', False), models.Q(('source', ''), _negated=True), ('source_id_3__isnull', False), models.Q(('source_id_3', ''), _negated=True)), fields=('source', 'source_id_3'), name='unique_question_source_id_3'),
        ),
    ]
