from django.contrib import admin
from django.db.models import Prefetch, Count
from djangoql.admin import DjangoQLSearchMixin
from import_export import resources
import easy

from exams.models import Exam
from users.models import User
from .models import Question, AnswerChoice, Answer
from .models import UserQuestionAnswer
from .models import UserQuestionStatus, UserQuestionAnswerStatus


EXAM_FK = exam_fk = easy.ForeignKeyAdminField('exam', display='exam.name', default='-')
QUESTION_FK = question_fk = easy.ForeignKeyAdminField('question', default='-')
USER_FK = user_fk = easy.ForeignKeyAdminField('user', display='user.username', default='-')

class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = False


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = False


@admin.register(Question)
class QuestionAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_select_related = ['program']
    list_display = [
        'id',
        'source_id',
        # 'source_id_2',
        # 'source_id_3',
        'module',
        # 'program',
        # 'stimulus',
        # 'stem',
        'difficulty',
        'answer_type',
        # 'explanation',
        # 'raw',
        'attempts',
        'users',
        'source',
        'source_order',
        'created',
        'modified',
    ]
    list_filter = [
        'program',
        'source',
        # 'created_at',
        # 'updated_at',
        'module',
        'difficulty',
        'answer_type',
    ]
    readonly_fields = ['source', 'source_id', 'source_id_2', 'source_id_3', 'uuid']
    raw_id_fields = ['added_by']
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [AnswerChoiceInline, AnswerInline]
    list_per_page = 1000

    attempts = easy.SimpleAdminField('attempts', short_description='Attempts', admin_order_field='attempts')
    users = easy.SimpleAdminField('users', short_description='Users', admin_order_field='users')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate count of attempts
        qs = (
            qs.annotate(
                attempts=Count('user_question_answer_set'),
                users=Count('user_question_answer_set__user', distinct=True),
            )
        )

        return qs


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    # list_select_related = ['question']
    list_display = [
        'id',
        'question_fk',
        # 'text',
        # 'explanation',
        'is_correct',
        'letter',
        'order',
    ]
    list_filter = [
        # 'question',
        'is_correct',
        'letter',
    ]
    list_per_page = 1000
    show_facets = admin.ShowFacets.ALWAYS
    raw_id_fields = ['question']

    question_fk = QUESTION_FK

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch('question', queryset=Question.objects.only('id')),
        )
        return qs


@admin.register(Answer)
class AnswerAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    # list_select_related = ['question']
    list_display = [
        'id',
        # 'question',
        'question_fk',
        'value',
        # 'explanation',
        'order'
    ]
    list_filter = []
    show_facets = admin.ShowFacets.ALWAYS
    raw_id_fields = ['question']
    list_per_page = 1000

    question_fk = QUESTION_FK

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch('question', queryset=Question.objects.only('id')),
        )
        return qs


@admin.register(UserQuestionAnswer)
class UserQuestionAnswerAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    # list_select_related = ['user', 'question', 'exam', 'answer_choice']
    list_display = [
        'id',
        # 'user', 'question', 'exam', 'answer_choice', 'answer',

        'user_fk',
        'exam_fk',
        'question_fk',
        'question_module',
        'answer_choice_fk',
        'answer',

        'is_correct',
        'time_given',
        'started_at',
        'answered_at',
    ]
    list_filter = [
        'is_correct',
        'question__module',
    ]
    show_facets = admin.ShowFacets.ALWAYS
    raw_id_fields = ['user', 'question', 'exam', 'answer_choice']
    readonly_fields = ['user']
    date_hierarchy = 'answered_at'
    list_per_page = 1000

    user_fk = USER_FK
    question_fk = QUESTION_FK
    exam_fk = EXAM_FK
    answer_choice_fk = easy.ForeignKeyAdminField('answer_choice', display='answer_choice.letter')

    question_module = easy.SimpleAdminField('question.module', short_description='Question Module')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch('question', queryset=Question.objects.only('id', 'module')),
            Prefetch('exam', queryset=Exam.objects.only('id', 'name')),
            Prefetch('answer_choice', queryset=AnswerChoice.objects.only('id', 'letter')),
            Prefetch('user', queryset=User.objects.only('id', 'username')),
        )
        return qs


@admin.register(UserQuestionStatus)
class UserQuestionStatusAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_select_related = ['user', 'question', 'exam']
    list_display = [
        'id',
        # 'user',
        # 'exam',
        # 'question',

        'user_fk',
        'exam_fk',
        'question_fk',
        'question_module',

        'is_marked_for_review',
        'marked_for_review_at',
        'unmarked_for_review_at',

        'is_skipped',
    ]
    list_filter = [
        'is_marked_for_review',
        'question__module',
    ]
    show_facets = admin.ShowFacets.ALWAYS
    raw_id_fields = ['user', 'exam', 'question']
    date_hierarchy = 'marked_for_review_at'
    list_per_page = 1000

    user_fk = USER_FK
    question_fk = QUESTION_FK
    exam_fk = EXAM_FK

    question_module = easy.SimpleAdminField('question.module', short_description='Question Module')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch('question', queryset=Question.objects.only('id', 'module')),
            Prefetch('exam', queryset=Exam.objects.only('id', 'name')),
            Prefetch('user', queryset=User.objects.only('id', 'username')),
        )
        return qs


