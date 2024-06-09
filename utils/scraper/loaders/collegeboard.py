from app.models import Program
from questions.models import Question, AnswerChoice, Answer


def load(data, program='sat'):
    source = 'cb'
    program = Program.objects.get(name__lower=program)

