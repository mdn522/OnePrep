from django.conf import settings


def theme_context(request):
    return {
        'DAISYUI_THEME': settings.DAISYUI_THEME
    }


def google_analytics_context(request):
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID
    }


def internet_blackout_context(request):
    return {
        'IS_BLACKOUT': settings.IS_BLACKOUT
    }
