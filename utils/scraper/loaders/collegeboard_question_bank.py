import json
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List
from sortedcontainers import SortedDict

from questions.models import Question, AnswerChoice, Answer
from exams.models import Exam, ExamQuestion
from ..loaders import Loader

import more_itertools
from rich import print


class CollegeBoardQuestionBankLoader(Loader):
    source = 'collegeboard_question_bank'
    modules = {
        'math': Question.Module.MATH,
        'english': Question.Module.ENGLISH,
    }
    difficulty_map = {
        'E': Question.Difficulty.EASY,
        'M': Question.Difficulty.MEDIUM,
        'H': Question.Difficulty.HARD,
    }
    difficulty_long_map = {
        'E': 'Easy',
        'M': 'Medium',
        'H': 'Hard',
    }
    answer_type_map = {
        'mcq': Question.AnswerType.MCQ,
        'Multiple Choice': Question.AnswerType.MCQ,
        'SPR': Question.AnswerType.SPR,
        'spr': Question.AnswerType.SPR,
    }

    # TODO Exam Based on Question Types, Difficulty, and Skills
    def load(self):
        program = self.get_program()
        questions_file = self.get_file('collegeboard', 'question_bank_digital_sat_questions.json')
        lookup_file = self.get_file('collegeboard', 'question_bank_digital_sat_lookup.json')
        missing_spr_answer_file = self.get_file('collegeboard', 'question_bank_digital_sat_question_missing_spr_answer.txt')
        missing_mcq_answer_file = self.get_file('collegeboard', 'question_bank_digital_sat_question_missing_mcq_answer.txt')

        with questions_file.open(encoding='utf-8') as fp:
            questions_raw = json.load(fp)

        with lookup_file.open(encoding='utf-8') as fp:
            lookup = json.load(fp)

            for k, v in [('mathLiveItems', 'math'), ('readingLiveItems', 'english')]:
                lookup[v] = lookup[k]
                del lookup[k]

        missing_spr_answers: Dict[str, List[str]] = {}
        with missing_spr_answer_file.open(encoding='utf-8') as fp:
            for line in fp.read().splitlines():
                if not line.strip():
                    continue
                q_id, answers = line.split('\t')
                missing_spr_answers[q_id] = answers.split(' ')
                # put integer then fraction then decimal
                # like: ['1', '1/2', '1.5']
                missing_spr_answers[q_id].sort(key=lambda x: (x.count('.'), x.count('/')))
        del answers

        missing_mcq_answers: Dict[str, str] = {}
        with missing_mcq_answer_file.open(encoding='utf-8') as fp:
            for line in fp.read().splitlines():
                if not line.strip():
                    continue
                q_id, answer = line.split('\t')
                missing_mcq_answers[q_id] = answer

        q_i = 0
        for q_id, q_meta in questions_raw.items():
            q_i += 1
            print('Question', q_i, 'of', len(questions_raw))

            content = q_meta['content']

            is_bluebook = q_meta['external_id'] in lookup[q_meta['module']]

            stimulus = content.get('stimulus') or content.get('body') or ''
            stem = content.get('stem') or content.get('prompt') or ''
            answer_type = content.get('type') or content['answer'].get('style')
            explanation = content.get('rationale') or content['answer'].get('rationale')
            assert answer_type
            assert explanation

            answer_type = self.answer_type_map[answer_type]

            answers_choices = []
            answers = []
            try:
                if answer_type == Question.AnswerType.MCQ:
                    if 'answerOptions' in content:
                        letters = ['A', 'B', 'C', 'D']
                        for ans_i, ans in enumerate(content['answerOptions']):
                            letter = letters[ans_i]
                            ans_text = ans.get('text') or ans.get('content')
                            ans_correct = None
                            if type(content.get('answerOptions')) == dict:
                                ans_correct = content.get('answerOptions').get('correct')
                            else:
                                ans_correct = content['correct_answer'][0]

                            answers_choices.append({
                                'letter': letter,
                                'text': ans_text,
                                'correct': letter in ans_correct,
                                'order': ans_i + 1,
                            })
                            assert answers_choices[-1]['text'] and answers_choices[-1]['correct'] is not None and answers_choices[-1]['letter']

                    if 'answer' in content:
                        correct_letter = content['answer'].get('correct_choice', '').upper()
                        if not correct_letter:
                            # print(q_id, q_meta['questionId'])
                            correct_letter = missing_mcq_answers[q_id]
                        assert correct_letter
                        for ans_letter, ans in SortedDict(content['answer']['choices']).items():
                            ans_letter = ans_letter.upper()
                            answers_choices.append({
                                'letter': ans_letter,
                                'text': ans['body'],
                                'correct': ans_letter == correct_letter,
                                'order': ord(ans_letter) - ord('A') + 1,
                            })
                            assert answers_choices[-1]['text'] and answers_choices[-1]['correct'] is not None and answers_choices[-1]['letter']

                    assert len(answers_choices) == 4

                elif answer_type == Question.AnswerType.SPR:
                    answers = content.get('correct_answer') or []
                    if len(answers) == 0:
                        answers = missing_spr_answers.get(q_id, [])

                    assert len(answers) > 0

                    # print(answers)
                else:
                    raise NotImplementedError
            except Exception as e:
                print('answers_choices', answers_choices)
                print('answers', answers)
                print(q_meta)
                raise e

            question_defaults = dict(
                source_id_2=q_meta['questionId'],
                source_raw_data=q_meta,
                source_order=q_i,

                module=self.modules[q_meta['module']],
                program=program,

                answer_type=answer_type,
                stimulus=stimulus,
                stem=stem,
                difficulty=self.difficulty_map[q_meta['difficulty']],
                explanation=explanation,
            )

            question, question_created = Question.objects.update_or_create(
                source=self.source,
                source_id=q_id,

                defaults=question_defaults
            )

            question.tags.add(
                'College Board',
                'Question Bank',
                'SAT',
                q_meta['module'].title(),
                {False: 'Non Bluebook', True: 'Bluebook'}[is_bluebook],
                # *{Question.AnswerType.MCQ: ['MCQ', 'Multiple Choice'], Question.AnswerType.SPR: ['SPR', 'Student Produced Response']}[answer_type],
                *(['MCQ', 'Multiple Choice'] if answer_type == Question.AnswerType.MCQ else ['SPR', 'Student Produced Response']),
                q_meta['primary_class_cd'], q_meta['primary_class_cd_desc'],
                q_meta['skill_cd'], q_meta['skill_desc'],
                self.difficulty_long_map[q_meta['difficulty']],
            )
            # question.skill_tags.add(
            #     q_meta['primary_class_cd'], q_meta['primary_class_cd_desc'],
            #     q_meta['skill_cd'], q_meta['skill_desc'],
            #     self.difficulty_long_map[q_meta['difficulty']],
            # )

            if answer_type == Question.AnswerType.MCQ:
                for ans in answers_choices:
                    answer_choice, answer_choice_created = AnswerChoice.objects.update_or_create(
                        question=question,
                        letter=ans['letter'],
                        defaults=dict(
                            text=ans['text'],
                            is_correct=ans['correct'],
                            order=ans['order'],
                        )
                    )
                # TODO remove old answer choices based on letter that does not exist in new answer choices
                question.answer_choice_set.exclude(letter__in=[ans['letter'] for ans in answers_choices]).delete()

            elif answer_type == Question.AnswerType.SPR:
                for ans_i, ans in enumerate(answers):
                    answer, answer_created = Answer.objects.update_or_create(
                        question=question,
                        value=ans,
                        defaults=dict(
                            order=ans_i + 1,
                        )
                    )
                # remove old answers based on text that does not exist in new answers
                question.answer_set.exclude(value__in=[ans for ans in answers]).delete()

