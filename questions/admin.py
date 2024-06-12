from django.contrib import admin

from .models import Question, AnswerChoice, Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'source_id',
        # 'source_id_2',
        # 'source_id_3',
        'module',
        'program',
        # 'stimulus',
        # 'stem',
        'difficulty',
        'answer_type',
        # 'explanation',
        # 'raw',
        'source',
        'source_order',
        'created',
        'modified',
        'added_by',
    )
    list_filter = (
        'program',
        # 'created_at',
        # 'updated_at',
        'added_by'
    )
    # date_hierarchy = 'created_at'


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question',
        'text',
        'explanation',
        'correct',
        'order',
    )
    list_filter = ('question', 'correct')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'value', 'explanation', 'order')
    list_filter = ('question',)
