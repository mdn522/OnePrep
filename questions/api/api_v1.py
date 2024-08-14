from datetime import timedelta, datetime
from typing import Optional

from django.utils import timezone
from django.utils.timezone import make_aware
from ninja import Router, Schema
from ninja.throttling import UserRateThrottle
from ninja.security import django_auth
from django.db import transaction
import zoneinfo

from utils.datetime import tz_now_w_ms
from ..models import Question, AnswerChoice, Answer
from ..models import UserQuestionAnswer, UserQuestionAnswerStatus, UserQuestionStatus

router = Router()


class MarkForReview(Schema):
    question_id: int
    exam_id: Optional[int] = None
    is_marked_for_review: bool


class SubmitAnswer(Schema):
    question_id: int
    exam_id: Optional[int] = None
    answer_choice_id: Optional[int] = None
    answer: Optional[str] = None

    started_at: Optional[int] = None
    time_given: Optional[int] = None


@router.post('/mark-for-review', auth=django_auth)
def question_mark_for_review(request, data: MarkForReview):
    user = request.user

    defaults = dict(is_marked_for_review=data.is_marked_for_review)
    if data.is_marked_for_review:
        defaults['marked_for_review_at'] = tz_now_w_ms()
        # defaults['unmarked_for_review_at'] = None
    else:
        defaults['unmarked_for_review_at'] = tz_now_w_ms()
        # defaults['marked_for_review_at'] = None

    with transaction.atomic():
        UserQuestionStatus.objects.update_or_create(
            user=user,
            question_id=data.question_id,
            exam_id=data.exam_id,
            defaults=defaults
        )

    return 200


class AnswerStatus(Schema):
    question_id: int
    exam_id: Optional[int] = None

    answer_choice_id: Optional[int] = None
    answer_spr: Optional[str] = None

    is_selected: bool
    is_deleted: bool


@router.post('/answers/status', auth=django_auth)
def answers_status_delete(request, data: AnswerStatus):
    user = request.user

    # check data.answer_choice_id
    if data.answer_choice_id:
        try:
            answer_choice = AnswerChoice.objects.get(id=data.answer_choice_id, question_id=data.question_id)
        except AnswerChoice.DoesNotExist:
            return 404

    user.question_answer_status_set.update_or_create(
        question_id=data.question_id,
        exam_id=data.exam_id,
        defaults=dict(
            is_deleted=data.is_deleted,
            is_selected=data.is_selected,
            answer_choice_id=data.answer_choice_id,
            answer_spr=data.answer_spr
        )
    )


@router.post('/answers/submit', throttle=[UserRateThrottle('4/s')], auth=django_auth)
def answers_submit(request, data: SubmitAnswer):
    user = request.user

    if data.answer_choice_id and data.answer:
        return 400

    if not data.answer_choice_id and not data.answer:
        return 400

    user_answer = UserQuestionAnswer(
        user=user,
        question_id=data.question_id,
        exam_id=data.exam_id,
        answered_at=tz_now_w_ms()
    )
    if data.started_at:  # UNIX timestamp to date
        user_answer.started_at = datetime.fromtimestamp(data.started_at, tz=zoneinfo.ZoneInfo("UTC"))
    if data.time_given:
        user_answer.time_given = timedelta(seconds=data.time_given)
    # check data.answer_choice_id
    if data.answer_choice_id:
        try:
            answer_choice = AnswerChoice.objects.get(id=data.answer_choice_id, question_id=data.question_id)
        except AnswerChoice.DoesNotExist:
            return 404

        # TODO group ID
        user_answer.answer_choice_id = data.answer_choice_id
        user_answer.is_correct = answer_choice.is_correct
    elif data.answer:
        question_answers = Answer.objects.filter(question_id=data.question_id).only('value')

        is_correct = False
        for qa in question_answers:
            if qa.value.strip() == data.answer:
                is_correct = True
                break

        user_answer.answer = data.answer
        user_answer.is_correct = is_correct

    if user_answer.answer_choice_id or user_answer.answer:
        user_answer.save()
        return 201
    else:
        return 400



# @router.get('/{event_id}')
# def event_details(request, event_id: int):
#     event = Event.objects.get(id=event_id)
#     return {"title": event.title, "details": event.details}
