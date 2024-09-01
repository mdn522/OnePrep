import json
from collections import namedtuple, OrderedDict, defaultdict
from typing import Any, Dict, List

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, Count, Field, Value, F, Min, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView, ListView

from core.models import SubqueryCount
from exams.models import Exam
from .models import Question, UserQuestionAnswer, UserQuestionStatus

# TODO remove later. temp mem cache
memcache = defaultdict(dict)


class QuestionListView(ListView):
    template_name = 'basic/pages/questions/question_list.html'
    model = Question
    context_object_name = 'questions'
    paginate_by = 50


class QuestionSetView(TemplateView):
    module_tag_map = {
        Question.Module.ENGLISH: 'English',
        Question.Module.MATH: 'Math',
    }

    set_stats = []

    def question_number(self, context, question):
        context['question_set_current_number'] = 'N/A'
        context['question_set_next_question_id'] = None
        context['question_set_previous_question_id'] = None
        for q_i, q in enumerate(context['question_set_questions']):
            if q['id'] == int(question.id):
                context['question_set_current_number'] = q_i + 1
            elif context['question_set_current_number'] == 'N/A':
                context['question_set_previous_question_id'] = q['id']
            elif context['question_set_current_number'] != 'N/A':
                context['question_set_next_question_id'] = q['id']
                break


class ExamQuestionSet(QuestionSetView):
    name = 'Exam'
    key = 'exam'
    filters = {}

    def filtered_queryset(self, exam_id):
        # exam = Exam.objects.get(id=exam_id)
        return Question.objects.filter(exam_question_set__exam=exam_id).order_by('exam_question_set__order').distinct()

    def get_question_context_data(self, question, request, context):
        question_set_filter = OrderedDict()

        exam_id = request.GET.get('exam_id')

        assert exam_id, 'Exam ID is required'

        exam = Exam.objects.annotate(question_count=Count("exam_question_set")).get(id=exam_id)

        question_set = request.GET.get('question_set')
        question_set_filter['question_set'] = question_set
        question_set_filter['exam_id'] = exam.id

        context['question_set_filter'] = question_set_filter
        context['question_set_name'] = exam.name
        context['question_set_key'] = f'exam'
        context['question_set_filter'] = {}
        context['question_set_args'] = urlencode(question_set_filter)
        context['question_set_back'] = False

        question_set_filtered_queryset = self.filtered_queryset(exam_id=exam.id).order_by('source_order').only('id', 'source_order', 'difficulty', 'module')
        context['question_set_questions'] = question_set_filtered_queryset

        context['set_stats'] = [
            {
                'text': 'Total Questions',
                'value': exam.question_count,
            },
        ]

        # context['question_set_questions'] = list(question_set_filtered_queryset.order_by('source_order').values('id', 'source_order', 'difficulty'))

        # self.question_number(context, question)


QuestionBankCategoryCategoryMap = namedtuple('QuestionBankCategoryCategoryMap', ['module', 'primary_class', 'skill', 'primary_class_cd', 'skill_cd'], defaults=(None,) * 5)


class QuestionBankCategoryListView(QuestionSetView):
    template_name = 'basic/pages/questions/set/question_bank_categories.html'  # TODO rename
    question_content_type_id = ContentType.objects.get_for_model(Question).id

    category_map = []

    def filtered_queryset(self):
        qs = Question.objects
        for tag in self.tag_filter:
            qs = qs.filter(tags__name=tag)

        qs = qs.distinct()
        return qs

    # noinspection PyUnresolvedReferences
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # flat tags from category map

        if memcache[self.key].get('flat_tags') is None:
            flat_tags = set([tag for category in self.category_map for tag in [category.module, category.primary_class, category.skill] if tag])
            flat_tags = (flat_tags - {'en', 'math'}) | {'English', 'Math'} # | {'Bluebook', 'Non Bluebook'}
            memcache[self.key]['flat_tags'] = flat_tags

        flat_tags = memcache[self.key]['flat_tags']

        # TODO Cache
        if memcache[self.key].get('tags_map') is None:
            tags = Question.tags.through.tag_model().objects.filter(
                name__in=self.tag_filter + list(flat_tags)
            )
            memcache[self.key]['tags_map'] = {tag.name: tag for tag in tags}

        tags_map = memcache[self.key]['tags_map']

        # print('tags_map', tags_map)

        question_set_filter = {}
        question_set_filtered_queryset = self.filtered_queryset()
        question_set_filtered_queryset = self.get_filter_from_args(self.request, question_set_filter, {}, question_set_filtered_queryset)
        # print('filter_from_args', question_set_filter)

        # print(len(question_set_filtered_queryset))

        counts = (Question.tags.through.objects.filter(
            # tag__name__in=self.tag_filter,
            object_id__in=question_set_filtered_queryset.values('id'),  # tags__name__in=['Bluebook']
            # TODO cache
            content_type_id=self.question_content_type_id,
        ).annotate(
            # tag_id_=F('tag_id'),
        ).aggregate(   # .distinct('object_id')
            count=Count('object_id', distinct=True),
            # module count
            **{
                f'{category.module}': Count('object_id', distinct=True, filter=Q(tag_id=tags_map[self.module_tag_map[category.module]].id))
                for category in self.category_map if category.primary_class is None and category.skill is None
            },
            # primary class count
            **{
                f'{category.module}_{category.primary_class_cd}': Count('object_id', distinct=True, filter=Q(tag_id=tags_map[category.primary_class].id))
                for category in self.category_map if category.primary_class and category.skill is None
            },
            # skill count
            **{
                f'{category.module}_{category.primary_class_cd}_{category.skill_cd}': Count('object_id', distinct=True, filter=Q(tag_id=tags_map[category.skill].id))
                for category in self.category_map if category.skill
            }
            # module first question source_order ordered by question.source_order; source order is in question model. not in tags model
            # **{
            #     f'{category.module}_first_question_id': Min('object_id',
            #                                                 filter=Q(tag_id=tags_map[module_tag_map[category.module]].id))
            # },
            # **{
            #     # Use subquery
            #     f'{category.module}_first_question_id': Subquery(self.filtered_queryset().filter(tags__name__in=[module_tag_map[category.module]]).order_by('source_order').values('id').annotate('min_id', Min('id')).values('min_id')[:1])
            #     for category in self.category_map if category.primary_class is None and category.skill is None
            # }
        ))

        counts_marked_for_review = (
            UserQuestionStatus.objects.filter(
                user=self.request.user if self.request.user.is_authenticated else None, exam=None,
                question_id__in=question_set_filtered_queryset.values('id'),
                is_marked_for_review=True
            ).aggregate(
                count=Count('question_id', distinct=True),
                # module count
                **{
                    f'{category.module}': Count('question_id', distinct=True, filter=Q(question__tags__id=tags_map[self.module_tag_map[category.module]].id))
                    for category in self.category_map if category.primary_class is None and category.skill is None
                },
                # primary class count
                **{
                    f'{category.module}_{category.primary_class_cd}': Count('question_id', distinct=True, filter=Q(question__tags__id=tags_map[category.primary_class].id))
                    for category in self.category_map if category.primary_class and category.skill is None
                },
                # skill count
                **{
                    f'{category.module}_{category.primary_class_cd}_{category.skill_cd}': Count('question_id', distinct=True, filter=Q(question__tags__id=tags_map[category.skill].id))
                    for category in self.category_map if category.skill
                }
            )
        )

        # print('counts', counts)
        # print('counts_marked_for_review', counts_marked_for_review)

        categories = []
        modules_args = {}

        question_set_filter_wo_modules: Dict = {**question_set_filter}
        if 'module' in question_set_filter_wo_modules:
            del question_set_filter_wo_modules['module']

        for key, value in counts.items():
            if key.count('_') != 2:
                continue

            m, pc, s = key.split('_')
            _m, _pc, _s = key.replace('$$$', ' ').split('_')

            categories.append({
                'module': _m,
                'module_count': counts[m],
                'module_marked_count': counts_marked_for_review[m],
                'module_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules| {'module': _m}),
                'primary_class': _pc,
                'primary_class_count': counts[m + '_' + pc],
                'primary_class_marked_count': counts_marked_for_review[m + '_' + pc],
                'primary_class_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules | {'module': _m, 'primary_class': _pc}),
                'skill': _s,
                'skill_count': counts[m + '_' + pc + '_' + s],
                'skill_marked_count': counts_marked_for_review[m + '_' + pc + '_' + s],
                'skill_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules| {'module': _m, 'primary_class': _pc, 'skill': _s}),
                # 'primary_class': [],
            })

            if m not in modules_args:
                modules_args[m] = urlencode({'question_set': self.key} | question_set_filter_wo_modules | {'module': m})

            # print('key', key)

        # print('terms', self.terms)
        # print('counts', counts)
        # print('categories', categories)
        # print('question_module_counts', question_module_counts)
        # print('question_counts', question_counts)
        # get first object as json
        # print('question_module_counts', question_module_counts[0].__dict__)

        context['url_name'] = self.url_name
        context['name'] = self.name
        context['question_set_key'] = self.key
        context['terms'] = self.terms
        context['counts'] = counts
        context['counts_marked_for_review'] = counts_marked_for_review
        context['categories'] = categories
        context['modules'] = ['en', 'math']
        context['modules_args'] = modules_args
        context['filters'] = self.filters
        context['current_filter'] = question_set_filter
        return context

    def get_question_context_data(self, question, request, context):
        question_set_filter = OrderedDict()
        question_set_filter_text = OrderedDict()

        question_set = request.GET.get('question_set')

        question_set_filter['question_set'] = question_set
        question_set_filtered_queryset = self.filtered_queryset().order_by('source_order').only('id', 'source_order', 'difficulty', 'module')
        # print('QuestionSetView', QuestionSetView.terms)
        question_set_filtered_queryset = self.get_filter_from_args(request, question_set_filter, question_set_filter_text, question_set_filtered_queryset)

        context['question_set_name'] = self.name
        context['question_set_key'] = self.key
        context['question_set_filter'] = question_set_filter
        context['question_set_filter_text'] = question_set_filter_text
        context['question_set_questions'] = question_set_filtered_queryset
        context['question_set_filters'] = self.filters  # TODO remove
        context['question_set_terms'] = self.terms # TODO remove
        # url encode using urllib
        context['question_set_args'] = urlencode(question_set_filter)
        context['question_set_categories_args'] = urlencode({k: v for k, v in question_set_filter.items() if k not in ['module', 'question_set', 'primary_class', 'skill']})
        context['question_set_back'] = True

        # print('question_set_args', context['question_set_args'])
        # print('question_set_categories_args', context['question_set_categories_args'])

        set_stats: List[Dict[str, Any]] = self.set_stats
        set_stats = [
            {
                'text': 'Total Questions',
                'value': question_set_filtered_queryset.count(),
            },
            {
                'text': 'Set Module',
                'value': question_set_filter_text['module']
            },
            {
                'text': 'Set Difficulty',
                'value': question_set_filter_text.get('difficulty', 'All')
            } if 'difficulty' in self.filters else None,
            {
                'text': 'Set Active',
                'value': question_set_filter_text.get('active', 'All')
            } if 'active' in self.filters else None,
            {
                'text': 'Set Domain',
                'value': question_set_filter_text.get('primary_class', 'All')
            },
            {
                'text': 'Set Skill',
                'value': question_set_filter_text.get('skill', 'All')
            },
            {
                'text': 'Set Marked For Review',
                'value': question_set_filter_text.get('marked_for_review', 'All')
            }
        ] + set_stats

        set_stats = [stat for stat in set_stats if stat is not None]

        for stat in set_stats:
            if 'value' not in stat and 'value_func' in stat:
                stat['value'] = stat['value_func'](context)

        context['set_stats'] = set_stats

        # print('question_set_current_number', context['question_set_current_number'])
        # print('question_set_next_question_id', context['question_set_next_question_id'])
        # print('question_set_previous_question_id', context['question_set_previous_question_id'])

        # Question Stat
        question_tags_names = question.tags.names()
        primary_class = [category.primary_class for category in self.category_map if category.primary_class and category.primary_class in question_tags_names][0]
        skill = [category.skill for category in self.category_map if category.skill and category.skill in question_tags_names][0]
        question_stats = [
            {
                'text': 'Domain',
                'value': self.terms.get(primary_class, primary_class),
            },
            {
                'text': 'Skill',
                'value': self.terms.get(skill, skill),
            },
        ]

        context['stats'] += question_stats

        # print('question_set_questions', context['question_set_questions'])
        # print('question_stats', question_stats)

    def get_filter_from_args(self, request, question_set_filter, question_set_filter_text, question_set_filtered_queryset=None):
        for filter_key, filter_data in self.filters.items():
            if 'orm_annotate' in filter_data:
                question_set_filtered_queryset = question_set_filtered_queryset.annotate(**filter_data['orm_annotate'](request))

            if 'items' in filter_data:
                item_value: Dict[str, Any] = request.GET.get(filter_key, filter_data.get('default'))
                if item_value is not None:
                    if question_set_filtered_queryset is not None:
                        if isinstance(filter_data['items'][item_value], dict):
                            question_set_filtered_queryset = question_set_filtered_queryset.filter(**filter_data['items'][item_value].get('filter', {}))
                    question_set_filter[filter_key] = item_value
                    if 'term' in filter_data['items'][item_value]:
                        question_set_filter_text[filter_key] = self.terms.get(item_value, item_value)
                    else:
                        if type(filter_data['items'][item_value]) == str:
                            question_set_filter_text[filter_key] = filter_data['items'][item_value]
                        else:
                            question_set_filter_text[filter_key] = filter_data['items'][item_value]['text']

            if 'choices' in filter_data:
                item_value = request.GET.get(filter_key, filter_data.get('default'))
                if item_value is not None:
                    if item_value not in map(str, filter_data['choices'].values):
                        continue
                    if question_set_filtered_queryset is not None:
                        question_set_filtered_queryset = question_set_filtered_queryset.filter(**{filter_data['orm_field']: item_value})
                    question_set_filter[filter_key] = item_value
                    question_set_filter_text[filter_key] = dict(filter_data['choices'].choices).get(item_value)

        return question_set_filtered_queryset




class CollegeBoardQuestionBankCategoryListView(QuestionBankCategoryListView):
    name = 'College Board Question Bank'
    key = 'college-board-question-bank'
    url_name = "questions:question-set-cbqb"
    tag_filter = ['College Board', 'Question Bank']
    terms = {'math': 'Math', 'en': 'English', 'english': 'English',
             'H': 'Algebra', 'H.C.': 'Linear equations in two variables', 'H.E.': 'Linear inequalities in one or two variables', 'H.D.': 'Systems of two linear equations in two variables', 'H.B.': 'Linear functions', 'H.A.': 'Linear equations in one variable', 'P': 'Advanced Math', 'P.C.': 'Nonlinear functions', 'P.A.': 'Equivalent expressions', 'P.B.': 'Nonlinear equations in one variable and systems of equations in two variables ', 'Q': 'Problem-Solving and Data Analysis', 'Q.F.': 'Inference from sample statistics and margin of error ', 'Q.A.': 'Ratios, rates, proportional relationships, and units', 'Q.E.': 'Probability and conditional probability', 'Q.B.': 'Percentages', 'Q.D.': 'Two-variable data: Models and scatterplots', 'Q.C.': 'One-variable data: Distributions and measures of center and spread', 'Q.G.': 'Evaluating statistical claims: Observational studies and experiments ', 'S': 'Geometry and Trigonometry', 'S.B.': 'Lines, angles, and triangles', 'S.C.': 'Right triangles and trigonometry', 'S.A.': 'Area and volume', 'S.D.': 'Circles',
             'INI': 'Information and Ideas', 'INF': 'Inferences', 'CID': 'Central Ideas and Details', 'COE': 'Command of Evidence', 'CAS': 'Craft and Structure', 'WIC': 'Words in Context', 'TSP': 'Text Structure and Purpose', 'CTC': 'Cross-Text Connections', 'EOI': 'Expression of Ideas', 'SYN': 'Rhetorical Synthesis', 'TRA': 'Transitions', 'SEC': 'Standard English Conventions', 'BOU': 'Boundaries', 'FSS': 'Form, Structure, and Sense',
             'bluebook-only': 'Bluebook Only', 'all': 'All', 'non-bluebook': 'Exclude Bluebook'}
    category_map = [
        QuestionBankCategoryCategoryMap(module='en', primary_class=None, skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='CAS', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='CAS', skill='CTC'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='CAS', skill='TSP'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='CAS', skill='WIC'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='EOI', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='EOI', skill='SYN'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='EOI', skill='TRA'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='INI', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='INI', skill='CID'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='INI', skill='COE'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='INI', skill='INF'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='SEC', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='SEC', skill='BOU'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='SEC', skill='FSS'),
        QuestionBankCategoryCategoryMap(module='math', primary_class=None, skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill='H.A.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill='H.B.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill='H.C.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill='H.D.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='H', skill='H.E.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='P', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='P', skill='P.A.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='P', skill='P.B.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='P', skill='P.C.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.A.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.B.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.C.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.D.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.E.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.F.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Q', skill='Q.G.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='S', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='S', skill='S.A.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='S', skill='S.B.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='S', skill='S.C.'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='S', skill='S.D.'),
    ]

    filters = {
        'module': {
            'text': 'Module',
            'choices': Question.Module,
            'orm_field': 'module',
        },
        'active': {
            'show': True,
            'text': 'Filter',
            # 'default': 'all',
            'items': OrderedDict([
                ('all', {'text': 'All'}),
                ('bluebook-only', {'text': 'Bluebook Only', 'filter': {'tags__name': 'Bluebook'}}),
                ('non-bluebook', {'text': 'Exclude Bluebook', 'filter': {'tags__name': 'Non Bluebook'}}),
            ]),
        },
        'difficulty': {
            'show': True,
            'text': 'Difficulty',
            'items': OrderedDict([('all', 'All')] + Question.Difficulty.choices),
            'choices': Question.Difficulty,
            'orm_field': 'difficulty',
        },
        'marked_for_review': {
            'show': True,
            'text': 'Marked For Review',
            'items': OrderedDict([
                ('all', {'text': 'All'}),
                ('true', {'text': 'Yes', 'filter': {'is_marked_for_review': True}}),
                ('false', {'text': 'No', 'filter': {'is_marked_for_review': False}})
            ]),
            # 'orm_field': 'is_marked_for_review',
            'orm_annotate': lambda request: {'is_marked_for_review': Value(False) if not request.user.is_authenticated else Coalesce(
                Subquery(UserQuestionStatus.objects.filter(user=request.user, exam=None, question_id=OuterRef('id')).values('is_marked_for_review')[:1]),
                Value(False)
            ),}
        },

        'primary_class': {
            'show': False,
            'text': 'Domain',
            'items': OrderedDict([('all', {'text', 'All'})] + [
                (category.primary_class, {'term': category.primary_class, 'filter': {'tags__name': category.primary_class}}) for category in category_map if category.primary_class
            ]),
        },
        'skill': {
            'show': False,
            'text': 'Skill',
            'items': OrderedDict([('all', {'text', 'All'})] + [
                (category.skill, {'term': category.skill, 'filter': {'tags__name': category.skill}}) for category in category_map if category.skill
            ]),
        },
    }

    tags_map = None
    flat_tags = None


class PrincetonReviewPracticeTestsQuestionBankCategoryListView(CollegeBoardQuestionBankCategoryListView):
    name = 'The Princeton Review Practice Tests Question Bank'
    key = 'princeton-review-practice-tests-question-bank'
    url_name = "questions:question-set-prptqb"
    tag_filter = ['The Princeton Review']

    terms = {'math': 'Math', 'en': 'English', 'english': 'English'}
    QuestionBankCategoryCategoryMap = namedtuple('CategoryMap', ['module', 'primary_class', 'skill', 'primary_class_cd', 'skill_cd'], defaults=(None,) * 5)
    category_map = [
        QuestionBankCategoryCategoryMap(module='en', primary_class=None, skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Vocabulary'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Purpose'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Retrieval'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Charts'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Main Ideas'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Dual Texts'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Claims'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Reading', skill='Conclusions'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Complete Sentences'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Connecting Clauses'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Lists'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Modifiers'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='No Punctuation'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Nouns'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Pronouns'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Punctuation with Describing Phrases'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rules', skill='Verbs'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rhetoric', skill=None),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rhetoric', skill='Transitions'),
        QuestionBankCategoryCategoryMap(module='en', primary_class='Writing Rhetoric', skill='Rhetorical Synthesis'),
        QuestionBankCategoryCategoryMap(module='math', primary_class=None, skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill='Coordinate Geometry'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill='Functions'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill='Linear Solving'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill='Nonlinear Solving'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Algebra', skill='Representation and Interpretation'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Problem-Solving and Data Analysis', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Problem-Solving and Data Analysis', skill='Proportional Relationships'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Problem-Solving and Data Analysis', skill='Working with Data'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Strategies', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Strategies', skill='Plugging In'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Strategies', skill='Plugging In the Answers'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Geometry and Trigonometry', skill=None),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Geometry and Trigonometry', skill='Advanced Coordinate Geometry'),
        QuestionBankCategoryCategoryMap(module='math', primary_class='Geometry and Trigonometry', skill='Geometry and Trigonometry'),
    ]

    filters = {
        'module': {
            'text': 'Module',
            'choices': Question.Module,
            'orm_field': 'module',
        },

        'marked_for_review': {
            'show': True,
            'text': 'Marked For Review',
            'items': OrderedDict([
                ('all', {'text': 'All'}),
                ('true', {'text': 'Yes', 'filter': {'is_marked_for_review': True}}),
                ('false', {'text': 'No', 'filter': {'is_marked_for_review': False}})
            ]),
            # 'orm_field': 'is_marked_for_review',
            'orm_annotate': lambda request: {'is_marked_for_review': Value(False) if not request.user.is_authenticated else Coalesce(
                Subquery(UserQuestionStatus.objects.filter(user=request.user, exam=None, question_id=OuterRef('id')).values('is_marked_for_review')[:1]),
                Value(False)
            ), }
        },

        'primary_class': {
            'show': False,
            'text': 'Domain',
            'items': OrderedDict([('all', {'text', 'All'})] + [
                (category.primary_class, {'term': category.primary_class, 'filter': {'tags__name': category.primary_class}}) for category in category_map if
                category.primary_class
            ]),
        },
        'skill': {
            'show': False,
            'text': 'Skill',
            'items': OrderedDict([('all', {'text', 'All'})] + [
                (category.skill, {'term': category.skill, 'filter': {'tags__name': category.skill}}) for category in category_map if category.skill
            ]),
        },
    }


question_sets = {
    CollegeBoardQuestionBankCategoryListView.key: CollegeBoardQuestionBankCategoryListView,
    PrincetonReviewPracticeTestsQuestionBankCategoryListView.key: PrincetonReviewPracticeTestsQuestionBankCategoryListView,
    ExamQuestionSet.key: ExamQuestionSet,
}

for c in [CollegeBoardQuestionBankCategoryListView, PrincetonReviewPracticeTestsQuestionBankCategoryListView]:
    for i in range(len(c.category_map)):
        cat = c.category_map[i]
        if cat.primary_class:
            cd = cat.primary_class.replace(' ', '$$$')
            c.category_map[i] = c.category_map[i]._replace(primary_class_cd=cd)
            if ' ' in cat.primary_class:
                c.terms[cd] = cat.primary_class

        if cat.skill:
            cd = cat.skill.replace(' ', '$$$')
            c.category_map[i] = c.category_map[i]._replace(skill_cd=cd)
            if ' ' in cat.skill:
                c.terms[cd] = cat.skill




@login_required
def question_set_first_question_view(request):
    question_set = request.GET.get('question_set')
    if question_set not in question_sets:
        return JsonResponse({'error': 'Invalid question set'}, status=400)

    QuestionSetView: CollegeBoardQuestionBankCategoryListView = question_sets[question_set]()
    question_set_filter = {}

    question_set_filtered_queryset = QuestionSetView.filtered_queryset().order_by('source_order')
    question_set_filtered_queryset = QuestionSetView.get_filter_from_args(request, question_set_filter, {}, question_set_filtered_queryset)

    try:
        first_question = question_set_filtered_queryset.first()
    except Question.DoesNotExist:
        return JsonResponse({'error': 'No questions found'}, status=400)

    # print('first_question', first_question)

    redirect_url = reverse('questions:detail', args=(first_question.id,))
    parameters = urlencode({'question_set': question_set} | question_set_filter)
    return redirect(f'{redirect_url}?{parameters}')

    # return Redirect
    # return HttpResponse(json.dumps(first_question, indent=4), content_type='application/json')


class QuestionDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'basic/pages/questions/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = Question.objects.prefetch_related("tags").only(*[
            'module', 'program', 'difficulty',
            'stimulus', 'stem', 'answer_type', 'explanation',
            'tags', 'skill_tags',
            # 'answer_choice_set__text', 'answer_choice_set__explanation', 'answer_choice_set__correct', 'answer_choice_set__order', 'answer_choice_set__letter',
        ]).get(pk=kwargs['pk'])
        context['question'] = question
        context['Question'] = Question
        context['questions_tags'] = [tag.name for tag in question.tags.all()]
        context['mathjax_inline_ds'] = not any([tag in ['College Board', 'The Princeton Review'] for tag in context['questions_tags']])
        context['answer_choices'] = list(question.answer_choice_set.only(*['id', 'text', 'letter', 'order', 'correct', 'explanation']).order_by('order').values())
        context['answers'] = list(question.answer_set.only(*['id', 'value', 'order', 'explanation']).order_by('order').values())

        try:
            context['question_status'] = UserQuestionStatus.objects.get(user=self.request.user, question=question, exam=None)
        except UserQuestionStatus.DoesNotExist:
            context['question_status'] = None

        # TODO choice letter
        context['user_answers'] = UserQuestionAnswer.objects.filter(user=self.request.user, question=question).values(
            'answer_choice', 'answer', 'is_correct', 'answered_at', 'time_given'
        ).order_by('answered_at')
        # Bucket them by incorrect correct then again bucket
        f = lambda: {'items': [], 'corrected': False, 'attempts': 0}
        context['user_answers_groups']: List = [f()]
        for user_answer in context['user_answers']:
            if context['user_answers_groups'][-1]['corrected']:
                # context['user_answers_groups'][-1]['items'].reverse()
                context['user_answers_groups'].append(f())

            if user_answer['is_correct']:
                context['user_answers_groups'][-1]['items'].append(user_answer)
                context['user_answers_groups'][-1]['corrected'] = True
            else:
                context['user_answers_groups'][-1]['items'].append(user_answer)
                context['user_answers_groups'][-1]['attempts'] += 1

        context['user_answers_groups'].reverse()

        # print('user_answers_groups', context['user_answers_groups'])

        # print('user_answers', context['user_answers'])
        # print('user_answers_groups', context['user_answers_groups'])

        # print('question', question.__dict__)

        context['stats'] = [
            {
                'text': 'Module',
                'value': question.get_module_display()
            },
        ]

        if question.difficulty is not None:
            context['stats'].append({
                'text': 'Difficulty',
                'value': question.get_difficulty_display()
            })

        # Question Set Support
        question_set = self.request.GET.get('question_set')

        if question_set and question_set in question_sets:
            context['is_question_set'] = True
            context['question_set'] = question_set

            QuestionSetView: CollegeBoardQuestionBankCategoryListView = question_sets[question_set]()
            context['question_set_name'] = QuestionSetView.name

            try:
                QuestionSetView.get_question_context_data(question, self.request, context)
            except Exception as e:
                # print(e)
                context['is_question_set'] = False

            # question_set_filtered_queryset = question_set_filtered_queryset.only('id', 'source_order', 'difficulty')
            question_set_filtered_queryset = context['question_set_questions']
            # add is_marked_for_review if it exists otherwise set it to false by default if none is found (exam=None)

            question_set_filtered_queryset = question_set_filtered_queryset.annotate(
                is_marked_for_review=Coalesce(
                    Subquery(UserQuestionStatus.objects.filter(user=self.request.user, exam=None, question_id=OuterRef('id')).values('is_marked_for_review')[:1]),
                    Value(False)
                ),
                last_answer_correct=Subquery(UserQuestionAnswer.objects.filter(user=self.request.user, exam=None, question_id=OuterRef('id')).order_by('-answered_at').values('is_correct')[:1]),
            )

            context['question_set_questions'] = list(question_set_filtered_queryset.order_by('source_order').values('id', 'source_order', 'difficulty', 'is_marked_for_review', 'last_answer_correct'))

            # print('question_set_questions', context['question_set_questions'])

            QuestionSetView.question_number(context, question)

            # print('question_set_filtered_queryset', question_set_filtered_queryset.__dict__)
            # print('count', question_set_filtered_queryset.count())
            # print('question_set_filter', question_set_filter)

            # print('filters',  QuestionSetView.filters)

        # print(question.__dict__)

        return context
