from datetime import timedelta

from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from core.models import SkillTagged
import uuid


class Exam(TimeStampedModel, models.Model):
    # class Type(models.TextChoices):
    #     MOCK = 'mock', 'Mock'
    #     PRACTICE = 'practice', 'Practice'
    #     TEST = 'test', 'Test'
    #     QUIZ = 'quiz', 'Quiz'
    #     DRILL = 'drill', 'Drill'
    #     EXAM = 'exam', 'Exam'

    # TODO module/ or use tags
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True, db_index=True, verbose_name='UUID')
    name = models.CharField(max_length=128)
    description = models.TextField(default='', blank=True)
    time = models.DurationField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    tags = TaggableManager(blank=True)
    skill_tags = TaggableManager(through=SkillTagged, blank=True)

    official = models.BooleanField(default=False)

    added_by = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)

    source = models.CharField(max_length=128, null=True, blank=True, default='')
    source_id = models.CharField(max_length=255, null=True, blank=True, default='')
    source_order = models.PositiveIntegerField(null=True)  # TODO UniqueConstraint

    prevent_copy = models.BooleanField(default=False)

    can_retake = models.BooleanField(default=True)
    retake_after = models.DateTimeField(null=True, blank=True)

    can_see_explanation = models.BooleanField(default=False)

    # TODO Program
    # TODO price/coins
    # Analytics

    class Meta:
        # verbose_name = 'Exam'
        constraints = [
            # unique source id if not null
            models.UniqueConstraint(
                fields=['source', 'source_id'],
                name='unique_exam_source_id',
                condition=(Q(source__isnull=False) & ~Q(source='')) & (Q(source_id__isnull=False) & ~Q(source_id=''))
            ),
            # models.UniqueConstraint(
            #     fields=['uuid'],
            #     name='unique_exam_uuid_if_not_null',
            #     condition=~Q(uuid=None)
            # )
        ]

    def __str__(self):
        return self.name


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_question_set')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE, related_name='exam_question_set')
    order = models.PositiveIntegerField()

    # can_see_explanation = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Exam Question'

        ordering = ['order']

        constraints = [
            # Constraints
            # A question can only be in one section of an exam
            models.UniqueConstraint(fields=['exam', 'question'], name='unique_exam_question'),
            # A question can only be in one order in a section of an exam
            models.UniqueConstraint(fields=['exam', 'order'], name='unique_exam_question_order'),
        ]

    def __str__(self):
        return f'{self.exam.name} - Question #{self.order}'


# TODO Exam Group

class UserExam(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        FINISHED = 2, 'Finished'

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_exam_set')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='user_exam_set')

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    time_given = models.DurationField(null=True, blank=True)

    # suggest me more columns
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)

    class Meta:
        constraints = [
            # Constraints
            # A user can only have one exam if retake is false. hardcode it

            # models.UniqueConstraint(fields=['user', 'exam'], name='unique_user_exam'),
        ]
        verbose_name = 'User Exam'

