from django.conf import settings
from ipware import get_client_ip
from qsessions.geoip import ip_to_location_info


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

def ip_address_context(request):
    user_ip = None
    try:
        user_ip = get_client_ip(request)[0]
        loc_info = ip_to_location_info(user_ip)
    except:
        loc_info = {}

    country_code = request.GET.get('country_code', '')
    country_code = country_code or (loc_info or {}).get('country_code', '').upper()
    return {
        'IP_ADDRESS': user_ip,
        'COUNTRY_CODE': 'BD' or country_code,
    }
