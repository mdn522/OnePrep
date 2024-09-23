from audioop import reverse
from typing import List, Any, Dict

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from djangoql.admin import DjangoQLSearchMixin

from questions.models import Question, AnswerChoice, Module
from users.forms import UserAdminChangeForm
from users.forms import UserAdminCreationForm
from users.models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.site.login = login_required(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(DjangoQLSearchMixin, auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    date_hierarchy = "date_joined"

    list_display = [
        "id",
        "email",
        "username",
        "name",
        "num_user_question_answers",
        "date_joined",
        "last_login",
        "is_staff",
        "is_superuser",
    ]
    list_display_links = [
        "id",
        "email",
        "username",
    ]
    list_per_page = 500
    list_max_show_all = 1000
    search_fields = ["name"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "name"),
            },
        ),
    )
    show_facets = admin.ShowFacets.ALWAYS

    def num_user_question_answers(self, obj):
        total = obj.num_user_question_answers
        correct = obj.num_user_question_answers_correct
        incorrect = obj.num_user_question_answers_incorrect
        english_total = obj.num_user_question_answers_english
        english_correct = obj.num_user_question_answers_english_correct
        english_incorrect = obj.num_user_question_answers_english_incorrect
        math_total = obj.num_user_question_answers_math
        math_correct = obj.num_user_question_answers_math_correct
        math_incorrect = obj.num_user_question_answers_math_incorrect

        if not total:
            return '-'

        title = f"{(correct / total) * 100:.2f}% / {(incorrect / total) * 100:.2f}%"
        if english_total:
            title += f"\nEnglish: {english_correct} ({(english_correct / english_total) * 100:.2f}%) / {english_incorrect} ({(english_incorrect / english_total) * 100:.2f}%)"
        if math_total:
            title += f"\nMath: {math_correct} ({(math_correct / math_total) * 100:.2f}%) / {math_incorrect} ({(math_incorrect / math_total) * 100:.2f}%)"

        html = f'<span title="{title}">'
        html += f'<span style="">{total}</span> / '
        # percentage in title
        html += f'<span style="color: #2ECC71;">{correct}</span> / '
        html += f'<span style="color: #E74C3C;">{incorrect}</span>'
        html += '</span>'
        return mark_safe(html)

    num_user_question_answers.label = "Attempts"
    num_user_question_answers.admin_order_field = 'num_user_question_answers'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # count of user question answers

        return queryset.annotate(
            num_user_question_answers=Count("question_answer_set__id", distinct=True),
            num_user_question_answers_correct=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__is_correct=True)),
            num_user_question_answers_incorrect=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__is_correct=False)),

            # English
            num_user_question_answers_english=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.ENGLISH)),
            num_user_question_answers_english_correct=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.ENGLISH, question_answer_set__is_correct=True)),
            num_user_question_answers_english_incorrect=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.ENGLISH, question_answer_set__is_correct=False)),

            # Math
            num_user_question_answers_math=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.MATH)),
            num_user_question_answers_math_correct=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.MATH, question_answer_set__is_correct=True)),
            num_user_question_answers_math_incorrect=Count("question_answer_set__id", distinct=True, filter=Q(question_answer_set__question__module=Module.MATH, question_answer_set__is_correct=False)),
        )

    actions = [
        'export_user_data'
    ]

    def export_user_data(self, request, queryset):
        def remove_keys(obj, keys: List[Any]):
            if isinstance(obj, dict):
                obj = {
                    key: remove_keys(value, keys)
                    for key, value in obj.items()
                    if key not in keys
                }
            elif isinstance(obj, list):
                obj = [remove_keys(item, keys) for item in obj]  # if item not in keys
            return obj

        queryset = queryset.prefetch_related(
            'question_status_set', 'question_answer_set',
            'question_status_set__question', 'question_answer_set__question',
            'question_answer_set__answer_choice',
        )
        data_all = {}

        for user in queryset:
            user: User

            questions: Dict[int, Question] = {}
            answer_choices: Dict[int, AnswerChoice] = {}

            dkeys = ['id', 'user_id', 'exam_id']
            data = {
                'username': user.username,
                'question_status_set': remove_keys(list(user.question_status_set.values()), dkeys),
                'question_answer_set': remove_keys(list(user.question_answer_set.values()), dkeys),
                'questions': {},
                'answer_choices': {},
            }

            for answer in user.question_answer_set.all():
                if answer.question.id not in questions:
                    questions[answer.question.id] = answer.question

                if answer.answer_choice and answer.answer_choice.id not in answer_choices:
                    answer_choices[answer.answer_choice.id] = answer.answer_choice

            for status in user.question_status_set.all():
                if status.question.id not in questions:
                    questions[status.question.id] = status.question

            for question in questions.values():
                data['questions'][question.id] = {
                    'source': question.source,
                    'source_id': question.source_id,
                }

            for answer_choice in answer_choices.values():
                data['answer_choices'][answer_choice.id] = {
                    'question_id': answer_choice.question_id,
                    'letter': answer_choice.letter,
                }

            # print('questions', questions)
            # print('answer_choice', answer_choices)
            # print(data)

            data_all[user.username] = data

        data_all['type'] = 'users'
        response = JsonResponse(data_all, json_dumps_params=dict(indent=4))
        return response

    export_user_data.short_description = "Export Data"
