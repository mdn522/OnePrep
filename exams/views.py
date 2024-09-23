import django_filters
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, F, OuterRef, Subquery, Q, PositiveIntegerField
from django.shortcuts import render
from django.views.generic import ListView

from core.models import SubqueryCount
from questions.models import Question, UserQuestionAnswer, UserQuestionStatus
from .models import Exam


class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Exam
        fields = ['source', 'module', 'official']


cache = {}

class ExamListView(ListView):
    model = Exam
    template_name = 'basic/pages/exams/exam_list.html'

    context_object_name = 'exams'

    paginate_by = 500

    # TODO user answers count
    # TODO user correct percentage
    # TODO user time spent

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None

        questions = Question.objects.filter(exam_question_set__exam=OuterRef('pk')).order_by('exam_question_set__order').values('id')
        question_status = (
            UserQuestionStatus.objects
                .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_marked_for_review=True)
                .annotate(count=Count('id'))
                .order_by('question__exam_question_set__exam')
                .values('count')
        )

        question_answer = (
            UserQuestionAnswer.objects
                .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_correct=True).distinct('question')
        )

        question_answer_incorrect = (
            UserQuestionAnswer.objects
                .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_correct=False).distinct('question')
        )

        qs = (
            Exam.objects
                .filter(is_active=True)  # TODO is_public=True
                .annotate(question_count=Count("exam_question_set"))
                .annotate(marked_for_review_count=SubqueryCount(question_status))
                .annotate(correct_count=SubqueryCount(question_answer))
                .annotate(incorrect_count=SubqueryCount(question_answer_incorrect))
                .annotate(first_question_id=Subquery(questions[:1]))
                .order_by('source', 'source_order', 'name')
        )


        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        filter = ExamFilter(self.request.GET, qs)
        ctx["filter"] = filter

        if 'sources' not in cache:
            sources = Exam.objects.filter(is_active=True).values_list('source', flat=True).order_by('source').distinct()  # TODO cache
            cache['sources'] = sources  # TODO Use better caching with timeout

        ctx['sources'] = cache['sources']
        ctx['sources_friendly_names'] = {
            'collegeboard_bluebook': 'College Board Bluebook',
            'sat_panda': 'SAT Panda',
            'princeton_review': 'The Princeton Review',
            'satmocks': 'SAT® Mocks',
            'test_ninjas': 'Test Ninjas',
        }
        return ctx


