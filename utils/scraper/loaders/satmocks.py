import json
import json_stream
import re
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from typing import List

from json_stream.base import StreamingJSONList, StreamingJSONObject

from questions.models import Question, AnswerChoice, Answer, Module
from exams.models import Exam, ExamQuestion
from ..loaders import Loader

import more_itertools
from rich import print


def unstream(value):
    if isinstance(value, StreamingJSONList):
        return [unstream(el) for el in value]
    elif isinstance(value, StreamingJSONObject):
        return {k: unstream(v) for (k,v) in value.items()}
    else:
        return value


class SATMocksLoader(Loader):
    program = 'sat'
    source = 'satmocks'

    subject_id_to_module_map = {
        1: Module.ENGLISH,
        2: Module.ENGLISH,
        3: Module.MATH,
        4: Module.MATH,
        5: Module.ENGLISH,
    }

    module_to_text = {
        Module.ENGLISH: 'English',
        Module.MATH: 'Math',
    }

    def load(self):
        program = self.get_program()

        practices_file = self.get_file('satmocks', 'satmocks_raw_data_practices.json')  # , base_path=Path(r'D:\Workspace\Python\Notebooks\SAT-Lab')

        durations = {
            'math': timedelta(minutes=35),
            'english': timedelta(minutes=32),
        }
        explanations_cache = {}

        # print(files)
        practices_raw_filtered = []

        # with practices_file.open(encoding='utf-8') as fp:
        #     practices_raw = json.load(fp)

        fp = practices_file.open(encoding='utf-8')
        practices_raw = json_stream.load(fp)

        # for practice_id in practices_raw.items():
        for practice_id, practice_root in practices_raw._iter_items():
            practice_root = unstream(practice_root)

            practice = practice_root['practice']
            practice_id = practice['id']
            # exam_raw = practice['exam']

            if practice['exam'] is None:
                continue

            try:
                # print(practice_id, practice['exam']['title'])
                pass
            except:
                print(practice_id)
                raise

            if any((s in practice['exam']['title'] if isinstance(s, str) else s.match(practice['exam']['title'])) for s in [
                "Barron's Digital SAT",
                "Kaplan Digital SAT Test",
                # "MADS Digital SAT",
                # "Princeton Review Digital SAT",
                # SATMocks Full Practice Test 1 English Module 2 (Linear)
                re.compile(r'SATMocks Full Practice Test \d+ (English|Math) Module \d+ \(Linear\)'),
                re.compile(r'The SAT® Practice Test #\d+ (English|Math) Module \d+ \(Linear\)'),
            ]):
                practices_raw_filtered.append(practice)
                print(practice_id, practice['exam']['title'], "Public: ", practice['exam'].get('is_public'))

        for practice in practices_raw_filtered:
            practice_id = practice['id']
            exam_raw = practice['exam']

            module = self.subject_id_to_module_map[practice['subject_id']]

            exam, exam_created = Exam.objects.update_or_create(
                # duration=durations[exam_raw['module']],
                source=self.source,
                source_id=f'practice_{practice_id}',
                defaults=dict(
                    is_public=True,
                    name=exam_raw['title'],
                    description=exam_raw.get('description') or '',
                    added_by=None,
                    official=False,
                )
            )

            exam.tags.add('SAT', 'SATMocks', 'Exam', self.module_to_text[module])

            print('Exam Created', exam, exam_created)

            for exam_question_data in exam_raw['exam_questions']:
                question_data = exam_question_data['question']

                # answer_type = {o: Question.AnswerType.MCQ, 1: Question.AnswerType.SPR}[question_data['sat_options'][0]['title'] is None]
                answer_type = {1: Question.AnswerType.MCQ, 0: Question.AnswerType.SPR}[any(letter in question_data['sat_answers'][0]['answers'] for letter in ["A", "B", "C", "D"])]

                explanation = question_data['explanation'] or ''
                if explanation:
                    explanations_cache[question_data['id']] = explanation
                elif question_data['id'] in explanations_cache:
                    explanation = explanations_cache[question_data['id']]

                question, question_created = Question.objects.update_or_create(
                    source=self.source,
                    source_id=question_data['id'],
                    defaults=dict(
                        stem=question_data['content'],
                        stimulus=(question_data['sat_passage'] or {}).get('content', ''),
                        explanation=explanation,
                        answer_type=answer_type,

                        module=module,
                        program=program,

                        source_order=int(exam_question_data['order']),
                        # source_raw_data=question_data,
                    )
                )

                question.tags.add(
                    'SATMocks', 'SAT', self.module_to_text[module],
                )

                if answer_type == Question.AnswerType.MCQ:
                    AnswerChoice.objects.filter(question=question).update(is_correct=False)

                    for sat_option in question_data['sat_options']:
                        # pop till we get a valid answer
                        while question_data['sat_answers'][0]['answers'][0] not in ['A', 'B', 'C', 'D']:
                            question_data['sat_answers'][0]['answers'].pop(0)

                        assert question_data['sat_answers'][0]['answers'][0] in ['A', 'B', 'C', 'D'], question_data['sat_answers'][0]['answers']

                        answer_choice, answer_choice_created = AnswerChoice.objects.update_or_create(
                            question=question,
                            letter=sat_option['letter'],
                            defaults=dict(
                                text=sat_option['title'],
                                is_correct=question_data['sat_answers'][0]['answers'][0] == sat_option['letter'],
                                order=sat_option['order'],
                            )
                        )

                if answer_type == Question.AnswerType.SPR:
                    for i, sat_answer in enumerate(question_data['sat_answers']):
                        answer, answer_created = Answer.objects.update_or_create(
                            question=question,
                            value=sat_answer['answers'][0].strip('`').strip("'").strip('"') if isinstance(sat_answer['answers'][0], str) else sat_answer['answers'][0],

                            defaults=dict(
                                order=i,
                            )
                        )

                exam_question, exam_question_created = ExamQuestion.objects.update_or_create(
                    exam=exam,
                    question=question,
                    defaults=dict(
                        order=int(exam_question_data['order']),
                    ),
                )

