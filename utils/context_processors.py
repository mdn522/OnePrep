from django.conf import settings


def internet_blackout_context(request):
    return {
        'IS_BLACKOUT': settings.IS_BLACKOUT
    }
