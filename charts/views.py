from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
def chart_view(request):
    user: User = request.user

    # dynamic past 15 days
    DAYS = 30
    answer_set = user \
        .question_answer_set \
        .filter(answered_at__gte=(timezone.now() - timezone.timedelta(days=DAYS)).date()) \
        .prefetch_related('question') \
        .only(*['answered_at', 'started_at', 'time_given', 'is_correct', 'question__module'])

    # print(get_date_range(timezone.now() - timezone.timedelta(days=DAYS), timezone.now()))
    x_axis = [dt.strftime('%Y-%m-%d') for dt in get_date_range(timezone.now() - timezone.timedelta(days=30 - 1), timezone.now())]
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
        pass

    print('answer_data', answer_data)

    return render(request, 'basic/pages/charts/index.html', context={
        'answer_data': answer_data
    })
