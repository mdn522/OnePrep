import json
from collections import defaultdict
from datetime import timedelta

from questions.models import Question, AnswerChoice, Answer, Module
from exams.models import Exam, ExamQuestion
from ..loaders import Loader

import more_itertools
from rich import print


class CollegeBoardBlueBookLoader(Loader):
    source = 'collegeboard_bluebook'

    def load(self):
        program = self.get_program()
        files = self.get_file_list('collegeboard', 'bluebook*.json')

        durations = {
            'math': timedelta(minutes=35),
            'english': timedelta(minutes=32),
        }

        # print(files)
        exams = defaultdict(lambda: {
            'english': [],
            'english_easy': [],
            'english_hard': [],
            'math': [],
            'math_easy': [],
            'math_hard': [],
        })

        for file in files:
            practice_no, module_english_difficulty, module_math_difficulty = file.stem.split('practice_')[1].split('_')
            print(file, practice_no, module_english_difficulty, module_math_difficulty)

            with file.open(encoding='utf-8') as fp:
                obj = json.load(fp)

            for module_obj in obj:
                module_name = {'reading': 'english'}.get(module_obj['id'], module_obj['id'])
                exams[practice_no]['name'] = 'Bluebook Practice #' + str(practice_no)
                exams[practice_no]['index'] = int(practice_no)
                questions = module_obj['items']
                questions_section_1, questions_section_2 = list(more_itertools.divide(2, questions))
                exams[practice_no][module_name] = list(questions_section_1)
                name_diff = module_name + '_' + {'english': module_english_difficulty, 'math': module_math_difficulty}[module_name]
                exams[practice_no][name_diff] = list(questions_section_2)

        # print(exams)

        for exam_index, exams_data in exams.items():
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
                    source_id='_'.join(list(filter(None, ['practice', str(exams_data['index']), module, diff]))),
                    defaults=dict(
                        is_public=True,
                        name=' - '.join(list(filter(None, [exams_data['name'], module.title(), diff.title()]))),
                        source_order=exams_data['index'],
                        added_by=None,
                        time=durations[module],
                        official=True,
                    )
                )

                exam.tags.add('College Board', 'Bluebook', 'Exam', 'SAT', module.title())

                print(exam, exam_created)

                for question_data in exam_data:
                    question, question_created = Question.objects.update_or_create(
                        source=self.source,
                        source_id=question_data['questionId'],
                        defaults=dict(
                            stem=question_data['prompt'],
                            stimulus=question_data['passage'].get('body', ''),
                            explanation=question_data['answer']['rationale'],
                            answer_type={'SPR': Question.AnswerType.SPR, 'Multiple Choice': Question.AnswerType.MCQ}[question_data['answer']['style']],

                            module={'english': Module.ENGLISH, 'math': Module.MATH}[module],
                            program=program,

                            source_order=int(question_data['displayNumber']),
                            source_raw_data=None,  # question_data,  # TODO strip keys
                        )
                    )

                    question.tags.add(
                        'College Board', 'Bluebook', 'Practice Test', 'SAT', module.title(),
                    )

                    if question_data['answer']['style'] == 'Multiple Choice':
                        for choice_letter, choice_data in question_data['answer']['choices'].items():
                            answer_choice, answer_choice_created = AnswerChoice.objects.update_or_create(
                                question=question,
                                letter=choice_letter,
                                defaults=dict(
                                    text=choice_data['body'],
                                    is_correct=question_data['answer']['correctChoice'] == choice_letter,
                                    order=ord(choice_letter) - ord('A') + 1,
                                )
                            )

                    if question_data['answer']['style'] == 'SPR':
                        for i, choice in enumerate(question_data['answer']['correctChoice'].split(', ')):
                            answer, answer_created = Answer.objects.update_or_create(
                                question=question,
                                value=choice,

                                defaults=dict(
                                    order=i,
                                )
                            )

                        # TODO remove any other answers

                    exam_question, exam_question_created = ExamQuestion.objects.update_or_create(
                        exam=exam,
                        question=question,
                        defaults=dict(
                            order=int(question_data['displayNumber']),
                        ),
                    )















