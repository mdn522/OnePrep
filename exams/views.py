from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, F, OuterRef, Subquery
from django.shortcuts import render
from django.views.generic import ListView

from questions.models import Question
from .models import Exam


class ExamListView(ListView):
    model = Exam
    template_name = 'basic/pages/exams/exam_list.html'

    context_object_name = 'exams'

    paginate_by = 500

    # TODO user answers count
    # TODO user correct answers count
    # TODO user correct percentage
    # TODO user time spent
    # TODO user marked for review count

    def get_queryset(self):
        questions = Question.objects.filter(exam_question_set__exam=OuterRef('pk')).order_by('exam_question_set__order').values('id')

        return (
            Exam.objects
                .filter(is_active=True)  # is_public=True
                .annotate(question_count=Count("exam_question_set"))
                .annotate(first_question_id=Subquery(questions[:1]))
                .order_by('source', 'source_order', 'name')
        )


