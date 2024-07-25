import re
from functools import reduce

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import render
import json
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt

from questions.models import Question, AnswerChoice, UserQuestionAnswer, UserQuestionStatus
from users.models import User


def parse_time(time_str):
    # parse this format into timedelta P0DT00H00M08S
    regex = re.compile(r'P((?P<days>\d+?)D)?T((?P<hours>\d+?)H)?((?P<minutes>\d+?)M)?((?P<seconds>\d+?)S)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


@staff_member_required
@csrf_exempt
def import_question_answer_and_status_view(request):
    logs = ''

    if request.method == 'POST':
        raw = request.POST.get('data')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = None

        if data:
            user = User.objects.get(username=data['username'])
            questions = {}
            questions_id_2_id = {}
            questions_qs = Question.objects.filter(reduce(lambda x, y: x | y, [Q(source=q['source'], source_id=q['source_id']) for q in data['questions'].values()]))
            for q in questions_qs:
                # find question in data
                for data_question_id, data_question in data['questions'].items():
                    if q.source == data_question['source'] and q.source_id == data_question['source_id']:
                        questions[q.id] = q
                        questions_id_2_id[data_question_id] = q.id
                        break

            questions_id_2_id = {int(k): v for k, v in questions_id_2_id.items()}

            answer_choices = {}
            answer_choices_id_2_id = {}
            answer_choices_qs = AnswerChoice.objects.filter(reduce(lambda x, y: x | y, [Q(question_id=questions_id_2_id[ac['question_id']], letter=ac['letter']) for ac in data['answer_choices'].values()]))

            for ac in answer_choices_qs:
                # find answer choice in data
                for data_answer_choice_id, data_answer_choice in data['answer_choices'].items():
                    if ac.question_id == questions_id_2_id[data_answer_choice['question_id']] and ac.letter == data_answer_choice['letter']:
                        answer_choices[ac.id] = ac
                        answer_choices_id_2_id[data_answer_choice_id] = ac.id
                        break

            answer_choices_id_2_id = {int(k): v for k, v in answer_choices_id_2_id.items()}

            logs += 'User Question Answer'
            for user_question_answer in data['question_answer_set']:
                vals = dict(
                    user=user,
                    question=questions[questions_id_2_id[user_question_answer['question_id']]],
                    exam=None,
                )

                if user_question_answer['answer_choice_id']:
                    vals['answer_choice'] = answer_choices[answer_choices_id_2_id[user_question_answer['answer_choice_id']]]

                defaults = {k: v for k, v in user_question_answer.items() if k not in ['question_id', 'answer_choice_id', 'exam_id']}
                for k, v in defaults.items():
                    if k.endswith('_at') and v is not None:
                        defaults[k] = datetime.fromisoformat(v)
                    if k == 'time_given':
                        defaults[k] = parse_time(v)

                vals.update(defaults)

                obj, created = UserQuestionAnswer.objects.update_or_create(**vals)
                logs += f'Question #{user_question_answer['question_id']} -> {questions_id_2_id[user_question_answer['question_id']]}: Created: {created}\n'
                print(vals)
                print(UserQuestionAnswer.objects.filter(**{k: v for k, v in vals.items() if k not in ['answer']}))
                # print(vals)

            logs += '\n'

            logs += 'User Question Status'
            for user_question_status in data['question_status_set']:
                vals = {
                    'user': user,
                    'question': questions[questions_id_2_id[user_question_status['question_id']]],
                    'exam': None,
                }

                defaults = {k: v for k, v in user_question_status.items() if k not in ['user_id', 'question_id', 'exam_id']}
                for k, v in defaults.items():
                    if k.endswith('_at') and v is not None:
                        defaults[k] = datetime.fromisoformat(v)

                obj, created = UserQuestionStatus.objects.update_or_create(**vals, defaults=defaults)
                logs += f'Question #{user_question_status['question_id']} -> {questions_id_2_id[user_question_status['question_id']]}: Created: {created}\n'

            # print('user', user)
            # print('questions', questions)
            # print('questions_id_2_id', questions_id_2_id)
            #
            # print('answer_choices', answer_choices)
            # print('answer_choices_id_2_id', answer_choices_id_2_id)

        # print('data:', data)
    return render(request, 'basic/pages/tools/import_question_answer_and_status.html', context={'logs': logs})
