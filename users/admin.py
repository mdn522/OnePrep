from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from users.forms import UserAdminChangeForm
from users.forms import UserAdminCreationForm
from users.models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.site.login = login_required(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
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
    list_display = [
        "id",
        "email",
        "username",
        "name",
        "num_user_question_answers",
        "is_superuser"
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # count of user question answers
        return queryset.annotate(
            num_user_question_answers=Count("question_answer_set__id", distinct=True)
        )
