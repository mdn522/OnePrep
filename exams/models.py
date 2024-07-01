from datetime import timedelta

from django.db import models
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from core.models import SkillTagged


class Exam(TimeStampedModel, models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(default='', blank=True)
    time = models.DurationField()

    tags = TaggableManager()
    skill_tags = TaggableManager(through=SkillTagged)

    official = models.BooleanField(default=False)

    added_by = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)

    source = models.CharField(max_length=24, null=True, blank=True)
    source_id = models.CharField(max_length=64, null=True)
    source_order = models.PositiveIntegerField(null=True)  # TODO UniqueConstraint

    prevent_copy = models.BooleanField(default=False)
    retake = models.BooleanField(default=True)
    retake_after = models.DateTimeField(null=True, blank=True)

    # TODO Program
    # TODO price/coins
    # Analytics

    class Meta:
        # verbose_name = 'Exam'
        constraints = [
            # unique source id if not null
            models.UniqueConstraint(fields=['source', 'source_id'], name='unique_exam_source_id', condition=models.Q(source__isnull=False) & models.Q(source_id__isnull=False)),
        ]

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_question_set')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE, related_name='exam_question_set')
    order = models.PositiveIntegerField()

    can_see_explanation = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Exam Question'

        constraints = [
            # Constraints
            # A question can only be in one section of an exam
            models.UniqueConstraint(fields=['exam', 'question'], name='unique_exam_question'),
            # A question can only be in one order in a section of an exam
            models.UniqueConstraint(fields=['exam', 'order'], name='unique_exam_question_order'),
        ]

    def __str__(self):
        return f'{self.exam.title} - Question #{self.order}'


# TODO Exam Group

class UserExam(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_exam_set')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='user_exam_set')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)

    class Status(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        FINISHED = 2, 'Finished'

    class Meta:
        constraints = [
            # Constraints
            # A user can only have one exam if retake is false. hardcode it

            # models.UniqueConstraint(fields=['user', 'exam'], name='unique_user_exam'),
        ]
        verbose_name = 'User Exam'
