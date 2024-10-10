from constance import config
from django.conf import settings
from django.core.cache import caches
from django.http import HttpRequest
from django.utils import timezone
from ipware import get_client_ip
from qsessions.geoip import ip_to_location_info

from users.models import Profile


def amount_to_days(amount):
    if amount > 0:
        return 30


def base_context(request: HttpRequest):
    ctx = {
        'CONFIG': config,
    }

    # donation context
    if not request.user.is_authenticated:
        ctx['DISABLE_DONATION_NOTICE'] = True

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            request.user.profile = Profile.objects.create(user=request.user)
            profile = request.user.profile

        if request.user.profile.disable_donation_notice:
            if request.user.profile.disable_donation_notice_until:
                if timezone.now() <= request.user.profile.disable_donation_notice_until:
                    ctx['DISABLE_DONATION_NOTICE'] = True
            else:
                ctx['DISABLE_DONATION_NOTICE'] = True

        mem_cache = caches['memory']
        donation_target = mem_cache.get('DONATION_TARGET')
        donation_amount = mem_cache.get('DONATION_AMOUNT')
        timeout = 60 * 5
        if donation_target is None:
            donation_target = config.DONATION_TARGET
            mem_cache.set('DONATION_TARGET', donation_target, timeout)
        if donation_amount is None:
            donation_amount = config.DONATION_AMOUNT
            mem_cache.set('DONATION_AMOUNT', donation_amount, timeout)

        ctx['DONATION_TARGET'] = donation_target
        ctx['DONATION_AMOUNT'] = donation_amount

        try:
            ctx['HIDE_DONATION_NOTICE'] = False
            if profile.has_donated:
                # hide if last donation was within 30 days
                if timezone.now() - profile.last_donated_at < timezone.timedelta(days=amount_to_days(profile.last_donation_amount)):
                    ctx['HIDE_DONATION_NOTICE'] = True
                    ctx['HAS_DONATED_RECENTLY'] = True
        except:
            pass

    return ctx

def theme_context(request: HttpRequest):
    ctx = {
        'DAISYUI_THEME': settings.DAISYUI_THEME
    }
    if request.user.is_authenticated:
        try:
            ctx['DAISYUI_THEME'] = request.user.profile.theme
        except:
            pass
    return ctx


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
