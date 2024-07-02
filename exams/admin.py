from django.contrib import admin
from django.db.models import Count
from djangoql.admin import DjangoQLSearchMixin

from .models import Exam, ExamQuestion


@admin.register(Exam)
class ExamAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'time',
        'official',
        'question_count',
        'added_by'
    ]
    list_filter = ['official', 'time']
    search_fields = [
        'title',
        'description',
        # 'added_by__username',
        'added_by__email'
    ]
    readonly_fields = ['source', 'source_id']

    @staticmethod
    def question_count(obj):
        return obj.question_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(question_count=Count("exam_question_set"))
        return queryset


@admin.register(ExamQuestion)
class ExamQuestionAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ['exam', 'question', 'order']
    list_filter = ['exam']
    search_fields = ['exam__title', 'question__stem']

    # TODO Question Details
