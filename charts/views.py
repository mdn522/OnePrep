from typing import Optional

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from questions.models import Question
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
        # raise 404
        raise Http404

    # dynamic past 15 days
    DAYS = 30
    try:
        DAYS = int(request.GET.get('days'))
    except:
        pass
    DAYS = min(DAYS, 90)

    date__gte = (timezone.now() - timezone.timedelta(days=DAYS)).date()

    # Attempts Chart
    answer_set = user \
        .question_answer_set \
        .filter(answered_at__gte=date__gte) \
        .prefetch_related('question') \
        .only(*['answered_at', 'started_at', 'time_given', 'is_correct', 'question__module'])

    # print(get_date_range(timezone.now() - timezone.timedelta(days=DAYS), timezone.now()))
    x_axis = [dt.strftime('%Y-%m-%d') for dt in get_date_range(timezone.now() - timezone.timedelta(days=DAYS - 1), timezone.now())]
    answer_data = {
        'x_axis': x_axis,
        Question.Module.MATH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
        Question.Module.ENGLISH.value: {
            0: [0] * DAYS,
            1: [0] * DAYS,
        },
    }
    for answer in answer_set:
        answer_data[answer.question.module][answer.is_correct][x_axis.index(answer.answered_at.strftime('%Y-%m-%d'))] += 1

    status_set = user \
        .question_status_set \
        .filter(Q(marked_for_review_at__gte=date__gte) | Q(unmarked_for_review_at__gte=date__gte)) \
        .prefetch_related('question') \
        .only(*['is_marked_for_review', 'marked_for_review_at', 'unmarked_for_review_at', 'question__module'])

    mark_data = {
        'x_axis': x_axis,
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
            mark_data[status.question.module][status.is_marked_for_review][x_index] += 1

    # print('answer_data', answer_data)

    return render(request, 'basic/pages/charts/index.html', context={
        'current_user': user,
        'answer_data': answer_data,
        'mark_data': mark_data,
    })
