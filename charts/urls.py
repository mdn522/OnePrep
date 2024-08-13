from django.urls import path

from . import views

app_name = 'charts'

urlpatterns = [
    path("user/<int:user_id>/charts/", views.chart_view, name="chart_with_user_id"),
    path("user/<str:username>/charts/", views.chart_view, name="chart_with_username"),
    path("user/charts/", views.chart_view, name="chart"),


    path("charts/user/<int:user_id>/exam/<int:exam_id>/basic-time", views.basic_exam_time_view),
    path("charts/user/<str:username>/exam/<int:exam_id>/basic-time", views.basic_exam_time_view),
    path("charts/user/exam/<int:exam_id>/basic-time", views.basic_exam_time_view, name="basic_exam_time"),
]
