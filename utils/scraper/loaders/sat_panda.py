import json
from datetime import timedelta

from questions.models import Question, AnswerChoice, Answer, Module
from exams.models import Exam, ExamQuestion
from ..loaders import Loader

from rich import print


class SATPandaLoader(Loader):
    source = 'sat_panda'

    def load(self, mock: bool = False):
        program = self.get_program()
        tests_file = self.get_file('sat_panda', 'tests.json')

        with tests_file.open(encoding='utf-8') as fp:
            tests = json.load(fp)

        test_order = 1
        for test_id, test in tests.items():
            test_name = test['name']

            if test_name.startswith('Digital '):
                test_name = test_name[8:]

            test_name = 'SAT Panda - ' + test_name

            print(test_id, test_name)

            is_full_test = len(test['sections']) == 4
            assert len(test['sections']) in [1, 4]

            for section_id, section in sorted(test['sections'].items()):
                if is_full_test:
                    exam_name = test_name + ' - ' + {'en': 'English', 'math': 'Math'}[section['module']] + ' Module ' + str(section_id[-1])
                else:
                    exam_name = test_name

                # print(section_id, exam_name)

                exam, exam_created = Exam.objects.update_or_create(
                    source=self.source,
                    source_id=section_id,
                    defaults=dict(
                        is_public=True,
                        is_active=True,
                        name=exam_name,
                        module=section['module'],
                        source_order=test_order,
                        added_by=None,
                        time=timedelta(minutes=section['time_min']),
                        official=False,
                    )
                )
                test_order += 1

                tags = ['SAT Panda', 'SAT', self.module_title[section['module']]]
                tags.append('Mock Test' if is_full_test else 'Practice Test')
                exam.tags.add(*tags)

                print(exam, exam_created)

                for question_i, question_data in section['questions'].items():
                    answer_type = {'spr': Question.AnswerType.SPR, 'mcq': Question.AnswerType.MCQ}[question_data['type']]

                    question_id = '_'.join([section_id, 'q', question_i])
                    # print(question_i, question_id)

                    question, question_created = Question.objects.update_or_create(
                        source=self.source,
                        source_id='_'.join([section_id, 'q', question_data['question_id']]),
                        defaults=dict(
                            stem=question_data['stem'],
                            stimulus=question_data.get('stimulus') or '',
                            explanation=question_data.get('explanation') or '',
                            answer_type=answer_type,

                            module=section['module'],
                            program=program,

                            source_order=question_i,
                            source_raw_data=None,
                        )
                    )

                    question_tags = ['SAT Panda', 'SAT', self.module_title[section['module']]]
                    question_tags.append('Mock Test' if is_full_test else 'Practice Test')
                    question.tags.add(*question_tags)

                    if answer_type == Question.AnswerType.MCQ:
                        for choice_i, choice_data in enumerate(question_data['answer_choices'].values()):
                            AnswerChoice.objects.update_or_create(
                                question=question,
                                letter=choice_data['letter'],
                                defaults=dict(
                                    text=choice_data['text'],
                                    is_correct=choice_data['letter'] == question_data.get('correct_answer_choice'),
                                    order=ord(choice_data['letter']) - ord('A') + 1,
                                )
                            )
                    elif answer_type == Question.AnswerType.SPR:
                        for choice_i, choice_data in enumerate(question_data['answers']):
                            Answer.objects.update_or_create(
                                question=question,
                                defaults=dict(
                                    value=choice_data.strip(),
                                    order=choice_i,
                                )
                            )

                    exam_question, exam_question_created = ExamQuestion.objects.update_or_create(
                        exam=exam,
                        question=question,
                        defaults=dict(
                            order=question_i,
                        ),
                    )
