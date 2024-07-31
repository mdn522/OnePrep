from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, F, OuterRef, Subquery, Q, PositiveIntegerField
from django.shortcuts import render
from django.views.generic import ListView

from questions.models import Question, UserQuestionAnswer, UserQuestionStatus
from .models import Exam


class SubqueryCount(Subquery):
    # Custom Count function to just perform simple count on any queryset without grouping.
    # https://stackoverflow.com/a/47371514/1164966
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = PositiveIntegerField()


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
        question_status = (
            UserQuestionStatus.objects
                .filter(question__exam_question_set__exam=OuterRef('pk'), user=self.request.user if self.request.user.is_authenticated else None, exam=None, is_marked_for_review=True)
                .annotate(count=Count('id'))
                .order_by('question__exam_question_set__exam')
                .values('count')
        )

        qs = (
            Exam.objects
                .filter(is_active=True)  # is_public=True
                .annotate(question_count=Count("exam_question_set"))
                .annotate(marked_for_review_count=SubqueryCount(question_status))
                .annotate(first_question_id=Subquery(questions[:1]))
                .order_by('source', 'source_order', 'name')
        )

        return qs


