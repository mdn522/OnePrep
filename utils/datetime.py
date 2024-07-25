from django.utils import timezone


def tz_now_w_ms():
    now = timezone.now()
    return now.replace(microsecond=int(now.microsecond / 1000))
