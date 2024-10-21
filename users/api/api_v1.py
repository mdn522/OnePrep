from datetime import timedelta, datetime
from typing import Optional

from django.utils import timezone
from django.utils.timezone import make_aware
from ninja import Router, Schema
from ninja.throttling import UserRateThrottle
from ninja.security import django_auth
from ..models import User, Profile

router = Router()

# switch api for prefetch_question_field
class PrefetchQuestionField(Schema):
    prefetch_question: bool


@router.post('/set-prefetch-question', throttle=[UserRateThrottle('4/s')], auth=django_auth)
def set_prefetch_question(request, data: PrefetchQuestionField):
    user = request.user
    profile = Profile.objects.get(user=user)
    profile.prefetch_question = data.prefetch_question
    profile.save()
    return 200
