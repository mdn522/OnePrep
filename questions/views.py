import json
from collections import namedtuple, OrderedDict
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

from exams.models import Exam
from .models import Question, UserQuestionAnswer, UserQuestionStatus


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


class CollegeBoardQuestionBankCategoryListView(QuestionSetView, TemplateView):
    template_name = 'basic/pages/questions/set/collegeboard_question_bank_categories.html'

    name = 'College Board Question Bank'
    key = 'college-board-question-bank'
    tag_filter = ['College Board', 'Question Bank']
    terms = {'math': 'Math', 'en': 'English', 'english': 'English',
             'H': 'Algebra', 'H.C.': 'Linear equations in two variables', 'H.E.': 'Linear inequalities in one or two variables', 'H.D.': 'Systems of two linear equations in two variables', 'H.B.': 'Linear functions', 'H.A.': 'Linear equations in one variable', 'P': 'Advanced Math', 'P.C.': 'Nonlinear functions', 'P.A.': 'Equivalent expressions', 'P.B.': 'Nonlinear equations in one variable and systems of equations in two variables ', 'Q': 'Problem-Solving and Data Analysis', 'Q.F.': 'Inference from sample statistics and margin of error ', 'Q.A.': 'Ratios, rates, proportional relationships, and units', 'Q.E.': 'Probability and conditional probability', 'Q.B.': 'Percentages', 'Q.D.': 'Two-variable data: Models and scatterplots', 'Q.C.': 'One-variable data: Distributions and measures of center and spread', 'Q.G.': 'Evaluating statistical claims: Observational studies and experiments ', 'S': 'Geometry and Trigonometry', 'S.B.': 'Lines, angles, and triangles', 'S.C.': 'Right triangles and trigonometry', 'S.A.': 'Area and volume', 'S.D.': 'Circles',
             'INI': 'Information and Ideas', 'INF': 'Inferences', 'CID': 'Central Ideas and Details', 'COE': 'Command of Evidence', 'CAS': 'Craft and Structure', 'WIC': 'Words in Context', 'TSP': 'Text Structure and Purpose', 'CTC': 'Cross-Text Connections', 'EOI': 'Expression of Ideas', 'SYN': 'Rhetorical Synthesis', 'TRA': 'Transitions', 'SEC': 'Standard English Conventions', 'BOU': 'Boundaries', 'FSS': 'Form, Structure, and Sense',
             'bluebook-only': 'Bluebook Only', 'all': 'All', 'non-bluebook': 'Exclude Bluebook'}
    CategoryMap = namedtuple('CategoryMap', ['module', 'primary_class', 'skill'])
    category_map = [
        CategoryMap(module='en', primary_class=None, skill=None),
        CategoryMap(module='en', primary_class='CAS', skill=None),
        CategoryMap(module='en', primary_class='CAS', skill='CTC'),
        CategoryMap(module='en', primary_class='CAS', skill='TSP'),
        CategoryMap(module='en', primary_class='CAS', skill='WIC'),
        CategoryMap(module='en', primary_class='EOI', skill=None),
        CategoryMap(module='en', primary_class='EOI', skill='SYN'),
        CategoryMap(module='en', primary_class='EOI', skill='TRA'),
        CategoryMap(module='en', primary_class='INI', skill=None),
        CategoryMap(module='en', primary_class='INI', skill='CID'),
        CategoryMap(module='en', primary_class='INI', skill='COE'),
        CategoryMap(module='en', primary_class='INI', skill='INF'),
        CategoryMap(module='en', primary_class='SEC', skill=None),
        CategoryMap(module='en', primary_class='SEC', skill='BOU'),
        CategoryMap(module='en', primary_class='SEC', skill='FSS'),
        CategoryMap(module='math', primary_class=None, skill=None),
        CategoryMap(module='math', primary_class='H', skill=None),
        CategoryMap(module='math', primary_class='H', skill='H.A.'),
        CategoryMap(module='math', primary_class='H', skill='H.B.'),
        CategoryMap(module='math', primary_class='H', skill='H.C.'),
        CategoryMap(module='math', primary_class='H', skill='H.D.'),
        CategoryMap(module='math', primary_class='H', skill='H.E.'),
        CategoryMap(module='math', primary_class='P', skill=None),
        CategoryMap(module='math', primary_class='P', skill='P.A.'),
        CategoryMap(module='math', primary_class='P', skill='P.B.'),
        CategoryMap(module='math', primary_class='P', skill='P.C.'),
        CategoryMap(module='math', primary_class='Q', skill=None),
        CategoryMap(module='math', primary_class='Q', skill='Q.A.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.B.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.C.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.D.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.E.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.F.'),
        CategoryMap(module='math', primary_class='Q', skill='Q.G.'),
        CategoryMap(module='math', primary_class='S', skill=None),
        CategoryMap(module='math', primary_class='S', skill='S.A.'),
        CategoryMap(module='math', primary_class='S', skill='S.B.'),
        CategoryMap(module='math', primary_class='S', skill='S.C.'),
        CategoryMap(module='math', primary_class='S', skill='S.D.'),
    ]
    set_stats = [
        # {
        #     'text': 'Set Domain',
        #     'value_func': lambda x: x['question'].source_raw_data['primary_class_cd_desc']
        # },
        # {
        #     'text': 'Set Skill',
        #     'value_func': lambda x: x['question'].source_raw_data['skill_desc']
        # },
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

    def filtered_queryset(self):
        return Question.objects.filter(tags__name__in=self.tag_filter).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # question_count = self.filtered_queryset().distinct().count()

        # get count of questions per module and also get first question id only
        # question_module_counts = (
        #     self.filtered_queryset()
        #     # .order_by('module')
        #     .values('module')
        #     .annotate(
        #         count=Count('pk', distinct=True),
        #         # get id of first question based on module without using min or max or subquery. order_by source_order and use parent queryset filter
        #         # first_question_id=F('pk'),
        #     )
        # )

        # question_counts = (
        #     # aggregate based category_map
        #     self.filtered_queryset().aggregate(
        #         total=Count('pk', distinct=True),
        #         **{
        #             f'{category.module}_{category.primary_class}_{category.skill}': Count('pk', distinct=True,
        #                                                                                   filter=Q(module=category.module) & (Q(tags__name__in=[category.primary_class]) if category.primary_class else Q()) & (Q(tags__name__in=[category.skill]) if category.skill else Q()))
        #             for category in self.category_map
        #         }
        #     )
        # )

        # flat tags from category map
        flat_tags = set([tag for category in self.category_map for tag in [category.module, category.primary_class, category.skill] if tag])
        flat_tags = (flat_tags - {'en', 'math'}) | {'English', 'Math'} | {'Bluebook', 'Non Bluebook'}

        tags = Question.tags.through.tag_model().objects.filter(
            name__in=self.tag_filter + list(flat_tags)
        )
        tags_map = {tag.name: tag for tag in tags}

        # print('tags', tags_map)

        question_set_filter = {}
        question_set_filtered_queryset = self.filtered_queryset()
        question_set_filtered_queryset = self.get_filter_from_args(self.request, question_set_filter, {}, question_set_filtered_queryset)
        # print('filter_from_args', question_set_filter)

        counts = (Question.tags.through.objects.filter(
            # tag__name__in=self.tag_filter,
            object_id__in=question_set_filtered_queryset.values('id'),  # tags__name__in=['Bluebook']
            content_type_id=ContentType.objects.get_for_model(Question).id,
        ).annotate(
            # tag_id_=F('tag_id'),
        ).aggregate(   # .distinct('object_id')
            count=Count('object_id', distinct=True),
            # module count
            **{
                f'{category.module}': Count('object_id', distinct=True,
                                            filter=Q(tag_id=tags_map[self.module_tag_map[category.module]].id))
                for category in self.category_map if category.primary_class is None and category.skill is None
            },
            # # primary class count
            **{
                f'{category.module}_{category.primary_class}': Count('object_id', distinct=True,
                                                                     filter=Q(tag_id=tags_map[category.primary_class].id))
                for category in self.category_map if category.primary_class and category.skill is None
            },
            # # skill count
            **{
                f'{category.module}_{category.primary_class}_{category.skill}':
                    Count('object_id',
                          distinct=True,
                          filter=Q(tag_id=tags_map[category.skill].id))
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

        categories = []
        modules_args = {}

        question_set_filter_wo_modules: Dict = {**question_set_filter}
        if 'module' in question_set_filter_wo_modules:
            del question_set_filter_wo_modules['module']

        for key, value in counts.items():
            if key.count('_') != 2:
                continue

            m, pc, s = key.split('_')

            categories.append({
                'module': m,
                'module_count': counts[m],
                'module_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules| {'module': m}),
                'primary_class': pc,
                'primary_class_count': counts[m + '_' + pc],
                'primary_class_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules | {'module': m, 'primary_class': pc}),
                'skill': s,
                'skill_count': counts[m + '_' + pc + '_' + s],
                'skill_args': urlencode({'question_set': self.key} | question_set_filter_wo_modules| {'module': m, 'primary_class': pc, 'skill': s}),
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

        context['question_set_name'] = self.name
        context['question_set_key'] = self.key
        context['terms'] = self.terms
        context['counts'] = counts
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
        context['question_set_filters'] = self.filters
        context['question_set_terms'] = self.terms
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
            },
            {
                'text': 'Set Active',
                'value': question_set_filter_text.get('active', 'All')
            },
            {
                'text': 'Set Domain',
                'value': question_set_filter_text.get('primary_class', 'All')
            },
            {
                'text': 'Set Skill',
                'value': question_set_filter_text.get('skill', 'All')
            },
        ] + set_stats

        for stat in set_stats:
            if 'value' not in stat and 'value_func' in stat:
                stat['value'] = stat['value_func'](context)

        context['set_stats'] = set_stats

        # context['question_set_questions'] = list(question_set_filtered_queryset.order_by('source_order').values('id', 'source_order', 'difficulty'))  # TODO user status
        #
        # self.question_number(context, question)

        # print('question_set_current_number', context['question_set_current_number'])
        # print('question_set_next_question_id', context['question_set_next_question_id'])
        # print('question_set_previous_question_id', context['question_set_previous_question_id'])

        # Question Stat
        question_tags_names = question.tags.names()
        question_stats = [
            {
                'text': 'Domain',
                'value': self.terms[[category.primary_class for category in self.category_map if category.primary_class and category.primary_class in question_tags_names][0]]
            },
            {
                'text': 'Skill',
                'value': self.terms[[category.skill for category in self.category_map if category.skill and category.skill in question_tags_names][0]]
            },
        ]

        context['stats'] += question_stats


        # print('question_set_questions', context['question_set_questions'])

        # print('question_stats', question_stats)

    def get_filter_from_args(self, request, question_set_filter, question_set_filter_text, question_set_filtered_queryset=None):
        for filter_key, filter_data in self.filters.items():
            if 'items' in filter_data:
                item_value: Dict[str, Any] = request.GET.get(filter_key, filter_data.get('default'))
                if item_value is not None:
                    if question_set_filtered_queryset is not None:
                        if isinstance(filter_data['items'][item_value], dict):
                            question_set_filtered_queryset = question_set_filtered_queryset.filter(**filter_data['items'][item_value].get('filter', {}))
                    question_set_filter[filter_key] = item_value
                    if 'term' in filter_data['items'][item_value]:
                        question_set_filter_text[filter_key] = self.terms[item_value]
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


question_sets = {
    CollegeBoardQuestionBankCategoryListView.key: CollegeBoardQuestionBankCategoryListView,
    ExamQuestionSet.key: ExamQuestionSet,
}


@login_required
def question_set_first_question_view(request):
    question_set = request.GET.get('question_set')
    if question_set not in question_sets:
        return JsonResponse({'error': 'Invalid question set'}, status=400)

    QuestionSetView: CollegeBoardQuestionBankCategoryListView = question_sets[question_set]()
    question_set_filter = {}

    question_set_filtered_queryset = QuestionSetView.filtered_queryset()
    question_set_filtered_queryset = QuestionSetView.get_filter_from_args(request, question_set_filter, {}, question_set_filtered_queryset)

    first_question = question_set_filtered_queryset.first()

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

        # TODO only
        question = Question.objects.prefetch_related("tags").only(*[
            'module', 'program', 'difficulty',
            'stimulus', 'stem', 'answer_type', 'explanation',
            'tags', 'skill_tags',
            # 'answer_choice_set__text', 'answer_choice_set__explanation', 'answer_choice_set__correct', 'answer_choice_set__order', 'answer_choice_set__letter',
        ]).get(pk=kwargs['pk'])
        context['question'] = question
        context['Question'] = Question
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
                context['user_answers_groups'].append(f())

            if user_answer['is_correct']:
                context['user_answers_groups'][-1]['items'].append(user_answer)
                context['user_answers_groups'][-1]['corrected'] = True
            else:
                context['user_answers_groups'][-1]['items'].append(user_answer)
                context['user_answers_groups'][-1]['attempts'] += 1

        context['user_answers_groups'].reverse()

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
