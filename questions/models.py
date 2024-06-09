from django.db import models

from app.models import Program


class Question(models.Model):
    class Module(models.TextChoices):
        ENGLISH = 'en', 'English'
        MATH = 'math', 'Math'

    class Difficulty(models.IntegerChoices):
        UNSPECIFIED = 0, 'Unspecified'
        EASY = 1, 'Easy'
        MEDIUM = 2, 'Medium'
        HARD = 3, 'Hard'

    class Type(models.TextChoices):
        MCQ = 'mcq', 'Multiple Choice'
        SPR = 'spr', 'SPR'

    source = models.CharField(max_length=24, null=True, blank=True)
    source_order = models.PositiveIntegerField()
    source_id = models.CharField(max_length=64, null=True)
    source_id_2 = models.CharField(max_length=64, null=True)
    source_id_3 = models.CharField(max_length=64, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'source_id'], name='unique_question_source_id', condition=models.Q(source__isnull=False) & models.Q(source_id__isnull=False)),
            models.UniqueConstraint(fields=['source', 'source_id_2'], name='unique_question_source_id_2', condition=models.Q(source__isnull=False) & models.Q(source_id_2__isnull=False)),
            models.UniqueConstraint(fields=['source', 'source_id_3'], name='unique_question_source_id_3', condition=models.Q(source__isnull=False) & models.Q(source_id_3__isnull=False)),

            models.Index(fields=['source'], name='index_question_source', condition=models.Q(source__isnull=False)),
            models.Index(fields=['source', 'source_id'], name='index_question_source_id', condition=models.Q(source__isnull=False) & models.Q(source_id__isnull=False)),
        ]

    module = models.CharField(choices=Module.choices, max_length=4)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    stimulus = models.TextField(default='')
    stem = models.TextField(default='')
    difficulty = models.IntegerField(choices=Difficulty.choices)
    type = models.CharField(max_length=24, default='', choices=Type.choices)
    explanation = models.TextField(default='')

    raw = models.JSONField(default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    added_by = models.ForeignKey('users.User', on_delete=models.CASCADE)


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    text = models.TextField()
    explanation = models.TextField(default='', blank=True)
    correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField()
    letter = models.CharField(max_length=1)

    class Meta:
        verbose_name = 'Answer Choice'
        constraints = [
            models.UniqueConstraint(fields=['question', 'order'], name='unique_question_answer_choice_order'),
            models.UniqueConstraint(fields=['question', 'letter'], name='unique_question_answer_choice_letter')
        ]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.CharField(max_length=24, null=True)
    explanation = models.TextField(default='', blank=True)
    order = models.PositiveSmallIntegerField()

    constraints = [
        models.UniqueConstraint(fields=['question', 'order'], name='unique_question_answer_order')
    ]
