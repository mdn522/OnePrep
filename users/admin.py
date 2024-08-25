from typing import List, Any, Dict

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from djangoql.admin import DjangoQLSearchMixin

from questions.models import Question, AnswerChoice
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

    def num_user_question_answers(self, obj):
        return obj.num_user_question_answers

    num_user_question_answers.label = "User Question Answers"
    num_user_question_answers.admin_order_field = 'num_user_question_answers'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # self.export_user_data(request, queryset)

        # count of user question answers
        return queryset.annotate(
            num_user_question_answers=Count("question_answer_set__id", distinct=True)
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
