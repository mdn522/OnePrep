import easy
from django.contrib import admin
from django.db.models import Count
from django_object_actions import DjangoObjectActions
from djangoql.admin import DjangoQLSearchMixin

from .models import Exam, ExamQuestion


@admin.register(Exam)
class ExamAdmin(DjangoQLSearchMixin, DjangoObjectActions, admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'time',
        'source',
        'source_id',
        'official',
        'is_public',
        'is_active',
        'question_count',
        'added_by'
    ]
    list_filter = ['official', 'is_public', 'is_active', 'source', 'time']
    search_fields = [
        'name',
        'description',
        # 'added_by__username',
        'added_by__email'
    ]
    readonly_fields = ['source', 'source_id']
    raw_id_fields = ['added_by']

    @staticmethod
    def question_count(obj):
        return obj.question_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(question_count=Count("exam_question_set"))
        return queryset

    def make_public(modeladmin, request, queryset):
        queryset.update(is_public=True)

    changelist_actions = ('make_public',)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = [
        'id',
        'exam_fk',
        'question_fk',
        'order'
    ]
    list_filter = []
    search_fields = ['exam__name', 'question__stem']
    raw_id_fields = ['exam', 'question']
    list_select_related = ['exam', 'question']

    question_fk = easy.ForeignKeyAdminField('question')
    exam_fk = easy.ForeignKeyAdminField('exam')

    # TODO Question Details
