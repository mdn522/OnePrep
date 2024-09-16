from allauth.account.models import EmailAddress
from django.contrib import admin
from django.db.models import Prefetch
from djangoql.admin import DjangoQLSearchMixin
import easy

from allauth.account.admin import EmailAddressAdmin
from qsessions.admin import SessionAdmin, Session
from django_login_history2.admin import ReadOnlyModelAdmin as LoginAdmin, Login as Login

from users.models import User

USER_FK = easy.ForeignKeyAdminField('user', display='user.username')

# allauth
class EmailAddressAdmin2(DjangoQLSearchMixin, EmailAddressAdmin):
    list_per_page = 500
    list_max_show_all = 1000
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = 'user__date_joined'

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(map(lambda s: {'user': 'user_fk'}.get(s, s), list_display)) + ['user_date_joined']
        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch('user', queryset=User.objects.only('id', 'username', 'date_joined')),
        )
        return qs

    def user_date_joined(self, obj):
        return obj.user.date_joined

    user_date_joined.short_description = 'Date Joined'


    user_fk = USER_FK

# QSessions
class SessionAdmin2(DjangoQLSearchMixin, SessionAdmin):
    raw_id_fields = ["user"]

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display) + []
        return list_display


# django_login_history2
class LoginAdmin2(DjangoQLSearchMixin, LoginAdmin):
    list_display = ['id', 'ip', 'user_fk', 'country_name', 'city', 'user_agent', 'created_at']
    list_display_links = ['id', 'ip']
    list_select_related = ['user']
    date_hierarchy = 'created_at'
    list_filter = ['country_name', 'city']
    raw_id_fields = ["user"]
    show_facets = admin.ShowFacets.ALWAYS

    user_fk = USER_FK

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin2)

admin.site.unregister(Session)
admin.site.unregister(Login)

admin.site.register(Login, LoginAdmin2)
admin.site.register(Session, SessionAdmin2)
