from collections import defaultdict, OrderedDict
from typing import Optional, List

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from exams.models import Exam, ExamQuestion
from questions.models import Question, UserQuestionAnswer, UserQuestionStatus
from users.models import User


def get_date_range(start_date, end_date):
    res = []
    current_date = start_date.date()
    end_date = end_date.date()
    while current_date <= end_date:
        res.append(current_date)
        current_date += timezone.timedelta(days=1)

    return res


@login_required
def chart_view(request, user_id=None, username=None):
    user: Optional[User] = None
    if not user_id and not username:
        user = request.user
    else:
        if user_id:
            user = get_object_or_404(User, id=user_id)
        elif username:
            user = get_object_or_404(User, username=username)

    if not user:
        raise Http404

    # dynamic past 30 days
    DAYS = 30
    try:
        DAYS = int(request.GET.get('days'))
    except:
        pass
    DAYS = min(DAYS, 90)
    MAX_TIME_GIVEN_LIMIT = 60 * 30  # 30 minutes
    try:
        MAX_TIME_GIVEN_LIMIT = int(request.GET.get('max_time_given_limit'))
    except:
        pass

    date__gte = (timezone.now() - timezone.timedelta(days=DAYS)).date()

    # Attempts Chart
    answer_set = user \
        .question_answer_set \
        .filter(answered_at__date__gt=date__gte) \
        .prefetch_related(
            Prefetch('question', queryset=Question.objects.only('module'))
        ) \
        .only(*['answered_at', 'started_at', 'time_given', 'is_correct', 'question_id', 'question__module', 'user_id'])

    # print(get_date_range(timezone.now() - timezone.timedelta(days=DAYS), timezone.now()))
    x_axis = [dt.strftime('%Y-%m-%d') for dt in get_date_range(timezone.now() - timezone.timedelta(days=DAYS - 1), timezone.now())]
    answer_data = {
        'x_axis': x_axis,
        'all': {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.MATH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.ENGLISH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
    }

    answer_data_unique = {
        'x_axis': x_axis,
        'all': {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.MATH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.ENGLISH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
    }
    answer_data_unique_questions_by_day = {
        0: [set()] * DAYS,
        1: [set()] * DAYS,
    }

    time_given_data = {
        'x_axis': x_axis,
        'all':  [0] * DAYS,
        Question.Module.MATH.value: [0] * DAYS,
        Question.Module.ENGLISH.value: [0] * DAYS,
    }

    for answer in answer_set:
        dts = answer.answered_at.strftime('%Y-%m-%d')
        index = x_axis.index(dts)
        answer_data['all'][answer.is_correct][index] += 1
        answer_data[answer.question.module][answer.is_correct][index] += 1

        if answer.question_id not in answer_data_unique_questions_by_day[answer.is_correct][index]:
            answer_data_unique['all'][answer.is_correct][index] += 1
            answer_data_unique[answer.question.module][answer.is_correct][index] += 1
            answer_data_unique_questions_by_day[answer.is_correct][index].add(answer.question_id)

        # if answer.time_given:
        #     time_given_data['all'][index] += min(answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)
        #     time_given_data[answer.question.module][index] += min(answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)

    # ----------------------------------------------------------------

    f = lambda: {'items': [], 'corrected': False, 'attempts': 0}
    answers_groups: List = [f()]
    for answer in answer_set:
        if answers_groups[-1]['corrected']:
            answers_groups.append(f())

        if answer.is_correct:
            answers_groups[-1]['items'].append(answer)
            answers_groups[-1]['corrected'] = True
        else:
            answers_groups[-1]['items'].append(answer)
            answers_groups[-1]['attempts'] += 1

    answers_groups.reverse()

    # print('answers_groups', answers_groups)
    for group in answers_groups:
        if not group['items']:
            continue
        group['items'].reverse()
        first_answer = group['items'][0]
        index = x_axis.index(first_answer.answered_at.strftime('%Y-%m-%d'))
        if group['corrected']:
            time_given_data['all'][index] += min(first_answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)
            time_given_data[first_answer.question.module][index] += min(first_answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)
        else:
            time_given_data['all'][index] += min(first_answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)
            time_given_data[first_answer.question.module][index] += min(first_answer.time_given.total_seconds(), MAX_TIME_GIVEN_LIMIT)

    # ----------------------------------------------------------------

    status_set = user \
        .question_status_set \
        .filter(Q(marked_for_review_at__date__gt=date__gte) | Q(unmarked_for_review_at__date__gt=date__gte)) \
        .prefetch_related(
            Prefetch('question', queryset=Question.objects.only('module'))
        ) \
        .only(*['is_marked_for_review', 'marked_for_review_at', 'unmarked_for_review_at', 'question__module', 'user_id'])

    mark_data = {
        'x_axis': x_axis,
        'all': {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.MATH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.ENGLISH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
    }

    for status in status_set:
        dt = ""
        if status.is_marked_for_review:
            dt = status.marked_for_review_at
        else:
            dt = status.unmarked_for_review_at
        if dt:
            dts = dt.strftime('%Y-%m-%d')
            x_index = x_axis.index(dts)
            if mark_data[status.question.module][status.is_marked_for_review][x_index] is None:
                mark_data[status.question.module][status.is_marked_for_review][x_index] = 0

            mark_data['all'][status.is_marked_for_review][x_index] += 1
            mark_data[status.question.module][status.is_marked_for_review][x_index] += 1

    # print('answer_data', answer_data)
    # print('answer_data_unique', answer_data_unique)

    return render(request, 'basic/pages/charts/index.html', context={
        'current_user': user,
        'answer_data': answer_data,
        'answer_data_unique': answer_data_unique,
        'mark_data': mark_data,
        'time_given_data': time_given_data,
    })


@login_required
def basic_exam_time_view(request, exam_id, user_id=None, username=None):
    exam = get_object_or_404(
        Exam.objects.prefetch_related(
            Prefetch('exam_question_set', queryset=ExamQuestion.objects.order_by('order')),
            Prefetch('exam_question_set__question', queryset=Question.objects.only(*['module']))),
        id=exam_id
    )

    user: Optional[User] = None
    if not user_id and not username:
        user = request.user
    else:
        if user_id:
            user = get_object_or_404(User, id=user_id)
        elif username:
            user = get_object_or_404(User, username=username)

    if not user:
        raise Http404

    ctx = {}

    exam_questions_answers = UserQuestionAnswer.objects \
        .filter(user_id=user.id, question_id__in=exam.exam_question_set.values_list('question_id', flat=True)) \
        .only(*['time_given', 'is_correct', 'started_at', 'answered_at', 'question_id', 'user_id']).order_by('answered_at')

    exam_questions_status = UserQuestionStatus.objects \
        .filter(user_id=user.id, question_id__in=exam.exam_question_set.values_list('question_id', flat=True)) \
        .only(*['is_marked_for_review', 'marked_for_review_at', 'unmarked_for_review_at', 'question_id', 'user_id'])

    exam_questions_set = exam.exam_question_set.all()

    questions_order_to_id = {question.order: question.question_id for question in exam_questions_set}
    questions_data = defaultdict(lambda: {
        'correct_count': 0, 'correct_times': [], 'correct_time_avg': 0,
        'incorrect_count': 0, 'incorrect_times': [], 'incorrect_time_avg': 0,
        'attempted_count': 0, 'attempted_times': [], 'attempted_time_avg': 0,
        'time': 0, 'answers': OrderedDict(), 'status': None
    })

    for question_answer in exam_questions_answers:
        questions_data[question_answer.question_id]['answers'][question_answer.id] = question_answer

        for k in (['correct'] if question_answer.is_correct else ['incorrect']) + ['attempted']:
            questions_data[question_answer.question_id][f'{k}_times'].append(question_answer.time_given.total_seconds())
            questions_data[question_answer.question_id][f'{k}_count'] += 1

    for question_status in exam_questions_status:
        questions_data[question_status.question_id]['status'] = question_status

    for q_id in questions_data.keys():
        question_data = questions_data[q_id]
        question_data['correct_time_avg'] = sum(question_data['correct_times']) / question_data['correct_count'] if question_data['correct_count'] else 0
        question_data['incorrect_time_avg'] = sum(question_data['incorrect_times']) / question_data['incorrect_count'] if question_data['incorrect_count'] else 0
        question_data['attempted_time_avg'] = sum(question_data['attempted_times']) / question_data['attempted_count'] if question_data['attempted_count'] else 0

    ctx['exam'] = exam
    ctx['questions_data'] = questions_data
    ctx['exam_questions_set'] = exam_questions_set
    correct_times = [v['correct_times'] for v in questions_data.values()]
    ctx['correct_count'] = sum([bool(v['correct_count']) for v in questions_data.values()])
    ctx['incorrect_count'] = sum([bool(v['incorrect_count']) for v in questions_data.values()])
    ctx['attempted_count'] = sum([bool(v['attempted_count']) for v in questions_data.values()])

    ctx['total_correct_time_max'] = sum([max(v, default=0) for v in correct_times])
    ctx['total_correct_time_min'] = sum([min(v, default=0) for v in correct_times])
    ctx['total_correct_time_max_avg'] = (ctx['total_correct_time_max'] / ctx['correct_count']) if ctx['correct_count'] else 0
    ctx['total_correct_time_min_avg'] = (ctx['total_correct_time_min'] / ctx['correct_count']) if ctx['correct_count'] else 0

    # Chart
    x_axis = [f'Q{order}' for order in questions_order_to_id.keys()]
    correct_times_data = {
        'x_axis': x_axis,
        # TODO Annotate Mark for review
        'correct_times_avg': [0] * len(x_axis),
        'correct_times_min': [0] * len(x_axis),
        'correct_times_max': [0] * len(x_axis),
    }
    for order, question_id in questions_order_to_id.items():
        correct_times_data['correct_times_avg'][order - 1] = questions_data[question_id]['correct_time_avg']
        correct_times_data['correct_times_min'][order - 1] = min(questions_data[question_id]['correct_times'], default=0)
        correct_times_data['correct_times_max'][order - 1] = max(questions_data[question_id]['correct_times'], default=0)

    ctx['correct_times_data'] = correct_times_data

    # print('exam_questions_answers', exam_questions_answers)
    # print('exam_questions_status', exam_questions_status)
    # print('exam_questions_set', exam_questions_set)
    # print('questions_data', questions_data)
    # print(ctx)

    ctx['current_user'] = user

    return render(request, 'basic/pages/charts/exam_chart.html', context=ctx)
