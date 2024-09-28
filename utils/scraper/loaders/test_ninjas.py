import json
from datetime import timedelta
from collections import OrderedDict
from typing import List, Dict

from exams.models import Exam, ExamQuestion
from questions.models import Module, Question, AnswerChoice, Answer
from ..loaders import Loader
from fractions import Fraction


class TestNinjasLoader(Loader):
    source = 'test_ninjas'

    domain_map = {
        'Standard English Convention': 'Standard English Conventions',
        'Problem Solving and Data Analysis': 'Problem-Solving and Data Analysis'
    }

    skill_map = {
        'Two-Variable Data': 'Two-variable Data',
        'Linear Equations in Two Variable': 'Linear equations in two variables',
        'Linear Equations in One Variable': 'Linear equations in one variable',
        'Cross-Text Connection': 'Cross-Text Connections',
        'Linear Functions': 'Linear functions',
        'Nonlinear Functions': 'Nonlinear functions',
        'Equivalent Expressions': 'Equivalent expressions',
        'Nonlinear Equations': 'Nonlinear equations',
    }

    # TODO strip domain and skill

    def load(self, mock: bool = False):
        program = self.get_program()

        durations = {
            'math': timedelta(minutes=35),
            'en': timedelta(minutes=32),
        }

        # title_prefixes = {
        #     'test'
        # }

        tests_full_file = self.get_file(self.source, 'tests_full.json')
        tests_english_file = self.get_file(self.source, 'tests_english.json')
        tests_math_file = self.get_file(self.source, 'tests_math.json')

        with tests_full_file.open(encoding='utf-8') as fp:
            tests_full = json.load(fp)

        with tests_english_file.open(encoding='utf-8') as fp:
            tests_english = json.load(fp)

        with tests_math_file.open(encoding='utf-8') as fp:
            tests_math = json.load(fp)

        sections = OrderedDict()

        section_map = {
            0: (Module.ENGLISH, 'English', ''),
            1: (Module.MATH, 'Math', ''),
            2: (Module.ENGLISH, 'English', 'Hard'),
            3: (Module.MATH, 'Math', 'Hard'),
            4: (Module.ENGLISH, 'English', 'Easy'),
            5: (Module.MATH, 'Math', 'Easy'),
        }

        for test_i, test in tests_full.items():
            test_n = int(test_i) + 1

            name = f"Test Ninjas - Full-length Practice Test #{test_n}"
            test_id = f"pt_fl_{test_n}"

            for section_i in [0, 4, 2, 1, 5, 3]:
                section = test[section_i]
                module, module_title, section_diff_name = section_map[section_i]
                section_name = f'{name} - {module_title}'
                section_id = f"{test_id}_{module}"
                if section_diff_name:
                    section_name += f' - {section_diff_name}'
                    section_id += f'_{section_diff_name.lower()}'

                # print(section_id, section_name)
                sections[section_id] = {
                    'index': test_n - 1,
                    'name': section_name,
                    'id': section_id,
                    'questions': section,
                    'module': module,
                }

        for section_tuple in [
            (tests_english, Module.ENGLISH, 'English'),
            (tests_math, Module.MATH, 'Math'),
        ]:
            module_sections, module, module_title = section_tuple = section_tuple
            module = section_tuple[1]
            module_title = section_tuple[2]

            for section_i, section in module_sections.items():
                section_n = int(section_i) + 1

                section_name = f"Test Ninjas - {module_title} Practice Test #{section_n}"
                section_id = f"pt_{module}_{section_n}"

                # print(section_id, section_name)
                sections[section_id] = {
                    'index': section_n - 1,
                    'name': section_name,
                    'id': section_id,
                    'questions': section,
                    'module': module,
                }

        source_order = 0
        for section_id, section in sections.items():
            # print(section_id, section['name'])
            source_order += 1
            exam, exam_created = Exam.objects.update_or_create(
                source=self.source,
                source_id=section_id,
                defaults=dict(
                    is_public=True,
                    is_active=True,
                    name=section['name'],
                    module=section['module'],
                    source_order=source_order,
                    added_by=None,
                    official=False,
                ),
            )

            exam_tags = ['Test Ninjas', 'Practice Test', 'SAT', self.module_title[exam.module]]
            if '_fl_' in section_id:
                exam_tags.append('Exam')
            exam.tags.add(*exam_tags)

            print('Exam', exam, exam_created)

            for question_i, question_data in enumerate(section['questions']):
                answer_type = {0: Question.AnswerType.SPR, 1: Question.AnswerType.MCQ}['choices' in question_data]
                if answer_type == Question.AnswerType.SPR:
                    # print(question_i, answer_type, question_data['correct_answer'], self.correct_answer(question_data['correct_answer'].strip()))
                    pass

                question_stem = get_stem_html(question_data, section['module'] == Module.MATH)
                question_stimulus = get_stimulus_html(question_data, section['module'] == Module.MATH)
                question_explanation = get_explanation_html(question_data)

                question, question_created = Question.objects.update_or_create(
                    source=self.source,
                    source_id=f"{section_id}_q_{question_i + 1}",
                    defaults=dict(
                        stem=question_stem,
                        stimulus=question_stimulus,
                        explanation=question_explanation,
                        answer_type=answer_type,

                        module=section['module'],
                        program=program,

                        source_order=question_i + 1,
                        source_raw_data=None,
                    ),
                )

                question_tags = ['Test Ninjas', 'Practice Test', 'SAT', self.module_title[question.module]]
                if '_fl_' in section_id:
                    question_tags.append('Exam')
                question.tags.add(*question_tags)
                #
                if answer_type == Question.AnswerType.MCQ:
                    for choice_letter, choice_text in question_data['choices'].items():
                        assert choice_letter in ['A', 'B', 'C', 'D']
                        AnswerChoice.objects.update_or_create(
                            question=question,
                            letter=choice_letter,
                            defaults=dict(
                                text=choice_text,
                                is_correct=choice_letter == question_data['correct_answer'],
                                order=ord(choice_letter) - ord('A') + 1,
                            )
                        )
                elif answer_type == Question.AnswerType.SPR:
                    answers = self.correct_answer(question_data['correct_answer'].strip())
                    assert answers
                    for choice_i, choice_data in enumerate(answers):
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

    def correct_answer(self, answer: str) -> str:
        answers = [answer]
        if '.' in answer:
            frac_answer = Fraction(answer)
            frac_answer_str = str(frac_answer)
            # 5 char if no negative sign else 6
            if len(frac_answer_str) <= 5 or (len(frac_answer_str) == 6 and frac_answer_str[0] == '-'):
                answers.append(frac_answer_str)

        answers.sort(key=lambda x: (x.count('.'), x.count('/')))
        return answers

def get_explanation_html(question):
    html = '<p class="tn-q-explanation">'
    html += f'<p class="whitespace-pre-line">{question["explanation"]}</p>'
    if 'distractor_explanation' in question:  # List[str]
        for distractor_explanation in question['distractor_explanation']:
            html += f'<p class="whitespace-pre-line">{distractor_explanation}</p>'

    html += '</p>'
    return html

def get_table_html(table):
    # headers[str], rows[[str]]
    html = '<table class="mb-5 tn-q-table">'
    # thead
    html += '<thead>'
    html += '<tr>'
    for header in table['headers']:
        html += f'<th>{header}</th>'
    html += '</tr>'
    html += '</thead>'
    # tbody
    html += '<tbody>'
    for row in table['rows']:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    return html

def get_image_html(image):
    # src, alt
    # assert image
    if not image:
        return ""
    return f'<img src="https://test-ninjas-sat-questions.s3.us-west-2.amazonaws.com/{image}" style="max-width: 100%; max-height: 300px;" class="tn-q-image">'

def get_quote_html(quote):
    # quote, author
    return f'''<p class="ml-4 whitespace-pre-line tn-q-quote">{quote}</p>'''

def get_passage_html(passage):
    # passage
    html = ""
    if type(passage) == str:
        if '•' in passage:  # Notes
            notes = passage.split('•')
            html = f'''<p class="tn-q-passage">{notes[0]}</p>'''
            notes_html = [f'<li class="tn-q-note">{note}</li>' for note in notes[1:]]
            html += f'''<ul class="tn-q-notes">{"".join(notes_html)}</ul>'''
        else:
            html = f'''<p class="tn-q-passage">{passage}</p>'''
    elif 'text_1' in passage:
        text_1 = passage['text_1']
        text_2 = passage['text_2']
        html = f'''<p class="tn-q-passage-texts"><p>Text 1</p><p class="tn-q-text-1 whitespace-pre-line">{text_1}</p><br><p>Text 2</p><p class="tn-q-text-2 whitespace-pre-line">{text_2}</p></p>'''
    assert html
    return html

def get_stimulus_html(question, is_math: bool = False):
    html = ""
    if 'table' in question:
        html += get_table_html(question['table'])
    if not is_math and 'image' in question:
        html += get_image_html(question['image'])
    if 'passage' in question:
        html += get_passage_html(question['passage'])
    if 'quote' in question:
        html += get_quote_html(question['quote'])
    return html

def get_stem_html(question, is_math: bool = False):
    html = ""
    if is_math and 'image' in question:
        html += get_image_html(question['image'])
    html += f'<p class="tn-q-question">{question["question"]}</p>'
    return f'''<p class="tn-q-stem">{html}<p>'''
