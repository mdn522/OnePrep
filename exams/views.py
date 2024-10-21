import time

import django_filters
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, F, OuterRef, Subquery, Q, PositiveIntegerField
from django.shortcuts import render
from django.views.generic import ListView

from core.models import SubqueryCount
from questions.models import Question, UserQuestionAnswer, UserQuestionStatus
from .models import Exam, ExamQuestion


class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Exam
        fields = ['source', 'module', 'official']


class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # Get the queryset however you usually would.  For example:
        queryset = super().get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.

        context['filterset'] = self.filterset
        return context


# cache = {}

class ExamListView(FilteredListView):
    model = Exam
    template_name = 'basic/pages/exams/exam_list.html'

    context_object_name = 'exams'
    filterset_class = ExamFilter
    paginate_by = 40

    # TODO user answers count
    # TODO user correct percentage
    # TODO user time spent

    def get_queryset(self):
        qs = super().get_queryset()
        qs = (
            qs
            # .annotate(parent_exam_id=F('id'))
            .filter(is_active=True).order_by('source', 'source_order', 'name')
        )  # TODO is_public=True
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # qs = self.get_queryset()
        # filter = ExamFilter(self.request.GET, qs)
        # ctx["filter"] = filter

        user = self.request.user if self.request.user.is_authenticated else None

        qs = ctx[self.get_context_object_name(None)]

        questions = Question.objects.filter(exam_question_set__exam=OuterRef('pk')).order_by('exam_question_set__order').values('id')
        question_status = (
            UserQuestionStatus.objects
            # .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_marked_for_review=True)
            .annotate(parent_exam_id=OuterRef('pk'))
            .filter(question_id__in=ExamQuestion.objects.filter(exam_id=OuterRef('parent_exam_id')).values('question_id'), user=user, exam=None, is_marked_for_review=True)
            # .annotate(count=Count('id'))
            # .order_by('question__exam_question_set__exam')
            # .distinct('question')
            .values('id')
        )

        question_answers = (
            UserQuestionAnswer.objects
            .filter(question_id__in=ExamQuestion.objects.filter(exam_id__in=qs.values('id')).values('question_id'), user=user, exam=None)
            .values('question_id')
        )
        # print(question_answers)
        # print(ExamQuestion.objects.filter(exam_id__in=qs.values('id')).values_list('question_id', flat=True))

        # exam_data = {
        #
        # }
        #
        # for

        # question_answers = (
        #     UserQuestionAnswer.objects
        #     # .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_correct=True)
        #     .annotate(parent_exam_id=OuterRef('pk'))
        #     .filter(question_id__in=ExamQuestion.objects.filter(exam_id=OuterRef('parent_exam_id')).values('question_id'), user=user, exam=None)
        #     .distinct('question').values('id')
        # )

        question_answer_correct = (
            UserQuestionAnswer.objects
            # .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_correct=True)
            .annotate(parent_exam_id=OuterRef('pk'))
            .filter(question_id__in=ExamQuestion.objects.filter(exam_id=OuterRef('parent_exam_id')).values('question_id'), user=user, exam=None, is_correct=True)
            .distinct('question').values('id')
        )

        question_answer_incorrect = (
            UserQuestionAnswer.objects
            # .filter(question__exam_question_set__exam=OuterRef('pk'), user=user, exam=None, is_correct=False)
            .annotate(parent_exam_id=OuterRef('pk'))
            .filter(question_id__in=ExamQuestion.objects.filter(exam_id=OuterRef('parent_exam_id')).values('question_id'), user=user, exam=None, is_correct=False)
            .distinct('question').values('id')
        )

        qs = qs.annotate(
            # TODO cache
            question_count=Count("exam_question_set"),
            marked_for_review_count=SubqueryCount(question_status),
            correct_count=SubqueryCount(question_answer_correct),
            incorrect_count=SubqueryCount(question_answer_incorrect),
            first_question_id=Subquery(questions[:1]),
        )

        ctx[self.get_context_object_name(None)] = qs

        from django.core.cache import caches

        mem_cache = caches['memory']

        # ctx['sources'] = mem_cache.get_or_set('sources', lambda: Exam.objects.filter(is_active=True).values_list('source', flat=True).order_by('source').distinct(), 300)
        ctx['count'] = mem_cache.get_or_set('exams__count', lambda: Exam.objects.filter(is_active=True).count(), 60)
        ctx['sources'] = mem_cache.get_or_set('exams__sources', lambda: Exam.objects.filter(is_active=True).values('source').annotate(count=Count('source')).order_by('source').values('source', 'count'), 300)

        # if 'sources' not in cache or (time.time() - cache['sources'][0]) > 300:
        #     sources = Exam.objects.filter(is_active=True).values_list('source', flat=True).order_by('source').distinct()  cache
        #     cache['sources'] = (time.time(), sources)   Use better caching with timeout

        # Add count along with source
        # ctx['sources'] = cache['sources'][1]
        ctx['sources_friendly_names'] = {
            'collegeboard_bluebook': 'College Board Bluebook',
            'sat_panda': 'SAT Panda',
            'princeton_review': 'The Princeton Review',
            'satmocks': 'SAT® Mocks',
            'test_ninjas': 'Test Ninjas',
        }
        return ctx


