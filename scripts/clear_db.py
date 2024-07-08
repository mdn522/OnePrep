import os.path as path
from io import StringIO
from collections import OrderedDict

from django.db import connection
from django.core.management import call_command

from questions.models import Question
from exams.models import Exam


# python manage.py runscript import_local_transactions --script-args "files/trx/transactions_sliced.json"

def reset_sequences():
    print('Resetting sequences...')

    # list of apps to reset
    app_names = ['questions', 'exams']

    for app_name in app_names:
        output = StringIO()
        call_command('sqlsequencereset', app_name, stdout=output, no_color=True)
        sql = output.getvalue()

        # Remove terminal color codes from sqlsequencereset output
        # ansi_escape = re.compile(r'\x1b[^m]*m')
        # sql = ansi_escape.sub('', sql)

        with connection.cursor() as cursor:
            cursor.execute(sql)

        output.close()

    print('Done')


def delete_all():
    Exam.objects.all().delete()
    Question.objects.all().delete()


def run(*args):
    delete_all()
    reset_sequences()
    print('Done')

