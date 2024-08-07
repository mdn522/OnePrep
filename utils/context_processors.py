from django.conf import settings


def google_analytics_context(request):
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID
    }


def internet_blackout_context(request):
    return {
        'IS_BLACKOUT': settings.IS_BLACKOUT
    }
