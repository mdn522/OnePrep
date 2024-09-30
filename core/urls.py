from django.urls import path


from . import views


# app_name = 'core'
urlpatterns = [
    path('tools/import-qans/', views.import_question_answer_and_status_view),
    path('tools/import-users/', views.import_user_csv_view),

    path('donate/', views.donate_view, name='donate'),
]

