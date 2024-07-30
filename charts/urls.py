from django.urls import path

from .views import chart_view

app_name = 'charts'

urlpatterns = [
    path("user/charts/", chart_view, name="chart"),
    path("user/<int:user_id>/charts/", chart_view, name="chart_with_user_id"),
    path("user/<str:username>/charts/", chart_view, name="chart_with_username"),
]
