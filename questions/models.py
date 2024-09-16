from django.db import models
from django.db.models import Q

from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
import uuid

from core.models import SkillTagged
from programs.models import Program


class Question(TimeStampedModel, models.Model):
    class Module(models.TextChoices):
        ENGLISH = 'en', 'English'
        MATH = 'math', 'Math'

    class Difficulty(models.TextChoices):
        # UNSPECIFIED = None, 'Unspecified'
        EASY = 'E', 'Easy'
        MEDIUM = 'M', 'Medium'
        HARD = 'H', 'Hard'

    class AnswerType(models.TextChoices):
        MCQ = 'mcq', 'Multiple Choice'
        SPR = 'spr', 'SPR'

    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True, db_index=True, verbose_name='UUID')

    source = models.CharField(max_length=128, null=True, blank=True, default='')
    source_id = models.CharField(max_length=255, null=True, blank=True, default='')
    source_id_2 = models.CharField(max_length=255, null=True, blank=True, default='')
    source_id_3 = models.CharField(max_length=255, null=True, blank=True, default='')
    source_order = models.PositiveIntegerField(null=True)  # TODO UniqueConstraint
    source_raw_data = models.JSONField(default=None, null=True, blank=True)

    module = models.CharField(choices=Module.choices, max_length=4)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    stimulus = models.TextField(default='', blank=True)
    stem = models.TextField(default='', blank=True)
    difficulty = models.CharField(choices=Difficulty.choices, max_length=2, null=True, blank=True)
    answer_type = models.CharField(max_length=24, default='', choices=AnswerType.choices)
    explanation = models.TextField(default='', blank=True)

    tags = TaggableManager()
    skill_tags = TaggableManager(through=SkillTagged, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    # Exam Values

    added_by = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            # Constraints
            # A question can only have one source and source_id if source is not null and source_id is not null
            models.UniqueConstraint(
                fields=['source', 'source_id'],
                name='unique_question_source_id',
                condition=(Q(source__isnull=False) & ~Q(source='')) & (Q(source_id__isnull=False) & ~Q(source_id=''))
            ),
            models.UniqueConstraint(
                fields=['source', 'source_id_2'],
                name='unique_question_source_id_2',
                condition=(Q(source__isnull=False) & ~Q(source='')) & (Q(source_id_2__isnull=False) & ~Q(source_id_2=''))
            ),
            models.UniqueConstraint(
                fields=['source', 'source_id_3'],
                name='unique_question_source_id_3',
                condition=(Q(source__isnull=False) & ~Q(source='')) & (Q(source_id_3__isnull=False) & ~Q(source_id_3=''))
            ),
            # models.UniqueConstraint(
            #     fields=['uuid'],
            #     name='unique_question_uuid_if_not_null',
            #     condition=~Q(uuid=None)
            # )

            # Indexes
            # Index for source
            # models.Index(fields=['source'], name='index_question_source', condition=Q(source__isnull=False)),
            # Index for source_id
            # models.Index(fields=['source', 'source_id'], name='index_question_source_id', condition=(Q(source__isnull=False) | ~Q(source='')) & (Q(source_id__isnull=False) | ~Q(source_id=''))),
        ]


class AnswerChoice(TimeStampedModel, models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_choice_set')

    text = models.TextField()
    explanation = models.TextField(default='', blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField()
    letter = models.CharField(max_length=1)

    class Meta:
        verbose_name = 'Answer Choice'
        constraints = [
            # Constraints
            # A question can only have one correct answer choice if correct is true
            models.UniqueConstraint(fields=['question', 'is_correct'], name='unique_question_answer_choice_correct', condition=models.Q(is_correct=True)),
            # A question can only have one answer choice with the same order
            models.UniqueConstraint(fields=['question', 'order'], name='unique_question_answer_choice_order'),
            # A question can only have one answer choice with the same letter
            models.UniqueConstraint(fields=['question', 'letter'], name='unique_question_answer_choice_letter'),
        ]


class Answer(TimeStampedModel, models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_set')
    value = models.CharField(max_length=24)
    explanation = models.TextField(default='', blank=True)
    order = models.PositiveSmallIntegerField()

    constraints = [
        # Constraints
        # A question can only have one answer with the same order
        # models.UniqueConstraint(fields=['question', 'order'], name='unique_question_answer_order'),
        # A question can only have one answer with the same value
        models.UniqueConstraint(fields=['question', 'value'], name='unique_question_answer_value'),
    ]


class UserQuestionAnswer(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='question_answer_set')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_question_answer_set')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, null=True, blank=True, related_name='user_question_answer_set')

    # ForeignKey AnswerChoice or Answer
    answer = models.CharField(max_length=6, null=True, blank=True)
    answer_choice = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE, null=True, blank=True)

    answer_group_id = models.CharField(max_length=64, null=True, blank=True)

    is_correct = models.BooleanField()
    time_given = models.DurationField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField()  # auto_now_add=True

    saw_explanation_before = models.BooleanField(default=False, blank=True, null=True)
    saw_explanation_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # Constraints
            # A user can only have one answer for a question in an exam if exam is not null
            models.UniqueConstraint(
                fields=['user', 'question', 'exam'],
                name='unique_user_question_answer_exam',
                condition=models.Q(exam__isnull=False)
            ),
        ]
        verbose_name = 'User Answer'


class UserQuestionStatus(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='question_status_set')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_question_status_set')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, null=True, blank=True, related_name='user_question_status_set')

    is_marked_for_review = models.BooleanField(default=False, blank=True)  # TODO retain
    marked_for_review_at = models.DateTimeField(null=True, blank=True)  # TODO retain
    unmarked_for_review_at = models.DateTimeField(null=True, blank=True)  # TODO retain

    is_skipped = models.BooleanField(default=False, blank=True)

    saw_explanation_before = models.BooleanField(default=False, blank=True)
    saw_explanation_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(default='', blank=True)

    class Meta:
        constraints = [
            # Constraints
            # A user can only have one status per question per exam
            models.UniqueConstraint(fields=['user', 'question', 'exam'], name='unique_user_question_status_exam'),
        ]

        verbose_name = 'User Question Status'
        verbose_name_plural = 'User Question Statuses'


class UserQuestionAnswerStatus(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='question_answer_status_set')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_question_answer_status_set')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, null=True, blank=True, related_name='user_question_answer_status_set')

    answer_choice = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE, null=True, blank=True)
    answer_spr = models.CharField(max_length=6, null=True, blank=True)

    # is_marked_for_review = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_selected = models.BooleanField(default=False, blank=True)

    class Meta:
        constraints = [
            # Constraints
            # A user can only have one status per question's answer per exam
            models.UniqueConstraint(
                fields=['user', 'question', 'exam', 'answer_choice'],
                name='unique_user_question_answer_status_exam',
                condition=models.Q(answer_choice__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'question', 'exam'],
                name='unique_user_question_answer_status_exam_spr',
                condition=models.Q(answer_choice__isnull=True)
            ),
        ]

        verbose_name = 'User Question Answer Status'
        verbose_name_plural = 'User Question Answer Statuses'
