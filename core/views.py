import re
from functools import reduce
import json
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from questions.models import Question, AnswerChoice, UserQuestionAnswer, UserQuestionStatus
from users.models import User

from io import StringIO
import csv

import sys
import traceback


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

    def parse_dts(dts):
        try:
            return datetime.fromisoformat(dts)
        except ValueError:
            from dateutil import parser
            return parser.parse(dts)

    if request.method == 'POST':
        raw = request.POST.get('data')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = None

        if data:
            try:
                data_list = data
                if data.get('type') == 'users':
                    del data['type']
                    data_list = data.values()
                else:
                    data_list = [data]

                for data in data_list:
                    user = User.objects.get(username=data['username'])
                    logs += "User: " + data['username'] + "\n"

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

                    logs += 'User Question Answer\n'
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
                                defaults[k] = parse_dts(v)
                            if k == 'time_given':
                                defaults[k] = parse_time(v)

                        vals.update(defaults)

                        obj, created = UserQuestionAnswer.objects.update_or_create(**vals)
                        # logs += f'Question #{user_question_answer['question_id']} -> {questions_id_2_id[user_question_answer["question_id"]]}: Created: {created}\n'
                        logs += 'Question #' + str(user_question_answer['question_id']) + ' -> ' + str(questions_id_2_id[user_question_answer["question_id"]]) + ': Created: ' + str(created) + '\n'
                        # print(vals)
                        # print(UserQuestionAnswer.objects.filter(**{k: v for k, v in vals.items() if k not in ['answer']}))
                        # print(vals)

                    logs += '\n'

                    logs += 'User Question Status\n'
                    for user_question_status in data['question_status_set']:
                        vals = {
                            'user': user,
                            'question': questions[questions_id_2_id[user_question_status['question_id']]],
                            'exam': None,
                        }

                        defaults = {k: v for k, v in user_question_status.items() if k not in ['user_id', 'question_id', 'exam_id']}
                        for k, v in defaults.items():
                            if k.endswith('_at') and v is not None:
                                defaults[k] = parse_dts(v)

                        obj, created = UserQuestionStatus.objects.update_or_create(**vals, defaults=defaults)
                        # logs += f'Question #{user_question_status['question_id']} -> {questions_id_2_id[user_question_status["question_id"]]}: Created: {created}\n'
                        logs += 'Question #' + str(user_question_status['question_id']) + ' -> ' + str(questions_id_2_id[user_question_status["question_id"]]) + ': Created: ' + str(created) + '\n'

                    # print('user', user)
                    # print('questions', questions)
                    # print('questions_id_2_id', questions_id_2_id)
                    #
                    # print('answer_choices', answer_choices)
                    # print('answer_choices_id_2_id', answer_choices_id_2_id)

                    logs += '\n\n'
            except Exception as e:
                type_, value_, traceback_ = sys.exc_info()
                logs += "Error:\n"
                logs += ''.join(traceback.format_exception(type_, value_, traceback_))
                # raise

        # print('data:', data)
    return render(request, 'basic/pages/tools/import_question_answer_and_status.html', context={'logs': logs})


@user_passes_test(lambda u: u.is_superuser)
@csrf_exempt
def import_user_csv_view(request):
    logs = ''

    if request.method == 'POST':
        users = []

        raw = request.POST.get('data')
        f = StringIO(raw)
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            logs += f"Username: {row['Username']}\n"
            users.append(User(
                username=row['Username'],
                email=row['Email'],
                password=make_password(row['Password']),
                name=row['Name'],
                is_active=True,
            ))

        usernames = [u.username for u in users]

        existing_users = User.objects.filter(username__in=usernames).only('username')
        existing_usernames = [u.username for u in existing_users]
        # remove user from users if username already exists
        users = [u for u in users if u.username not in existing_usernames]

        User.objects.bulk_create(users)

    return render(request, 'basic/pages/tools/import_bulk_user.html', context={'logs': logs})
