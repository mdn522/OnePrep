from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin
import easy

from qsessions.admin import SessionAdmin, Session
from django_login_history2.admin import ReadOnlyModelAdmin as LoginAdmin, Login as Login
# SessionAdmin.list_display = ['pk']

class SessionAdmin2(DjangoQLSearchMixin, SessionAdmin):

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display) + []
        return list_display

class LoginAdmin2(DjangoQLSearchMixin, LoginAdmin):
    list_display = ['id', 'ip', 'user_fk', 'country_name', 'city', 'user_agent', 'created_at']
    list_display_links = ['id', 'ip']
    list_select_related = ['user']
    date_hierarchy = 'created_at'
    list_filter = ['country_name', 'city']
    show_facets = admin.ShowFacets.ALWAYS

    user_fk = easy.ForeignKeyAdminField('user', display='user.username')

admin.site.unregister(Session)
admin.site.unregister(Login)

admin.site.register(Login, LoginAdmin2)
admin.site.register(Session, SessionAdmin2)
