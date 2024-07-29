import json
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from django.utils.text import slugify

from questions.models import Question, AnswerChoice, Answer
from exams.models import Exam, ExamQuestion
from ..loaders import Loader

import more_itertools
from rich import print


class PrincetonReviewLoader(Loader):
    program = 'sat'
    source = 'princeton_review'

    def load(self):
        program = self.get_program()
        # TODO path
        exams_file = self.get_file('princeton_review', 'exams.json')  # base_path=Path(r'D:\Workspace\Python\Notebooks\SAT-Lab')

        durations = {
            'math': timedelta(minutes=35),
            'english': timedelta(minutes=32),
        }

        with exams_file.open(encoding='utf-8') as fp:
            exams: dict[str, dict] = json.load(fp)

        exam_order = 1
        for exam_name, exams_data in exams.items():
            exam_name = exam_name
            for module, diff, exam_data in [
                ('english', '', exams_data['english']),
                ('english', 'easy', exams_data['english_easy']),
                ('english', 'hard', exams_data['english_hard']),
                ('math', '', exams_data['math']),
                ('math', 'easy', exams_data['math_easy']),
                ('math', 'hard', exams_data['math_hard']),
            ]:
                exam, exam_created = Exam.objects.update_or_create(
                    source=self.source,
                    source_id='_'.join(list(filter(None, [slugify(exam_name).replace('-', '_'), module, diff]))),
                    defaults=dict(
                        is_public=True,
                        is_active=True,
                        name='The Princeton Review ' + ' - '.join(list(filter(None, [exam_name, module.title(), diff.title()]))),
                        source_order=exam_order,
                        added_by=None,
                        time=durations[module],
                        official=False,
                    )
                )
                exam_order += 1

                exam.tags.add('The Princeton Review', 'Exam', 'SAT', module.title())

                print(exam, exam_created)

                for question_i, question_data in enumerate(exam_data):
                    answer_type = {0: Question.AnswerType.SPR, 1: Question.AnswerType.MCQ}['answer_choices' in question_data]

                    question, question_created = Question.objects.update_or_create(
                        source=self.source,
                        source_id=question_data['id'],
                        defaults=dict(
                            stem=question_data['stem'],
                            stimulus=question_data['stimulus'] or '',
                            explanation=question_data['explanation'],
                            answer_type=answer_type,

                            module={'english': Question.Module.ENGLISH, 'math': Question.Module.MATH}[module],
                            program=program,

                            source_order=question_i + 1,
                            source_raw_data=None,  # TODO strip keys
                        )
                    )

                    question.tags.add(
                        'The Princeton Review', 'SAT', module.title(),
                        *question_data['concepts']
                    )

                    if answer_type == Question.AnswerType.MCQ:
                        for choice_data in question_data['answer_choices']:
                            answer_choice, answer_choice_created = AnswerChoice.objects.update_or_create(
                                question=question,
                                letter=choice_data['letter'],
                                defaults=dict(
                                    text=choice_data['text'],
                                    is_correct=choice_data['is_correct'],
                                    order=choice_data['order'],
                                )
                            )
                    elif answer_type == Question.AnswerType.SPR:
                        for choice_i, choice in enumerate(question_data['answers']):
                            answer, answer_created = Answer.objects.update_or_create(
                                question=question,
                                value=choice,
                                defaults=dict(
                                    order=choice_i,
                                )
                            )

                    exam_question, exam_question_created = ExamQuestion.objects.update_or_create(
                        exam=exam,
                        question=question,
                        defaults=dict(
                            order=question_i + 1,
                        ),
                    )











