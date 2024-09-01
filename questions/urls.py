from django.urls import path
from . import views


app_name = 'questions'
urlpatterns = [
    path('question-set/first-question/', views.question_set_first_question_view, name='set-first-question'),

    path('question-set/college-board-question-bank/', views.CollegeBoardQuestionBankCategoryListView.as_view(), name='question-set-cbqb'),
    path('question-set/princeton-review-practice-tests-question-bank/', views.PrincetonReviewPracticeTestsQuestionBankCategoryListView.as_view(), name='question-set-prptqb'),
    path('question-set/<str:question_set>/', views.QuestionSetView.as_view(), name='question-set'),
    # first question
    # path('questions/', views.QuestionListView.as_view(), name='question_list'),
    #
    path('question/<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
]

