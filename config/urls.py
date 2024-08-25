# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView

admin.site.site_header = "OnePrep Admin"
admin.site.site_title = "OnePrep Admin Portal"
admin.site.index_title = "Welcome to OnePrep Admin Portal"

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),

    path("", include("core.urls")),
    path("", include("exams.urls", namespace="exams")),
    path("", include("questions.urls", namespace="questions")),
    path("", include("charts.urls", namespace="charts")),

    path("api/", include("api.urls")),

    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),

    # User management
    path("users/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here

    path("", TemplateView.as_view(template_name="basic/pages/home.html"), name="home"),


    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),


    # path('silk/', include('silk.urls', namespace='silk'))
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
