from django.urls import path

from . import views

app_name = 'exams'

urlpatterns = [
    path('exams/', views.ExamListView.as_view(), name='list'),
]
