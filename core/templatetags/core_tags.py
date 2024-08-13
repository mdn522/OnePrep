from datetime import timedelta

from django import template
from django.utils.http import urlencode

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

import json

register = template.Library()


@register.filter
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return mark_safe(serialize('json', obj))
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))


@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value


@register.filter
def get_item(dictionary, key):
    # print(key)
    # print(dictionary)
    value = dictionary.get(key)
    # print('value', value)
    return value


@register.filter
def dj_urlencode(value):
    return urlencode(value)


@register.filter
def merge_dict(dict1, dict2):
    return {**dict1, **dict2}


@register.filter
def get_dict_from_kv(k, v):
    return {k: v}


# @register.filter
# def dict_update_kv(dict1, dict2):
#     return {**dict1, **dict2}


@register.filter
def duration(td):
    g_num = lambda s, n: s + 's' if n > 1 else s

    if isinstance(td, int) or isinstance(td, float):
        td = timedelta(seconds=td)

    total_seconds = int(td.total_seconds())

    days = total_seconds // 86400
    remaining_hours = total_seconds % 86400
    remaining_minutes = remaining_hours % 3600
    hours = remaining_hours // 3600
    minutes = remaining_minutes // 60
    seconds = remaining_minutes % 60

    days_str = f'{days} {g_num("day", days)} ' if days else ''
    hours_str = f'{hours} {g_num("hour", hours)} ' if hours else ''
    minutes_str = f'{minutes} {g_num("minute", minutes)} ' if minutes else ''
    seconds_str = f'{seconds} {g_num("second", seconds)}' if seconds and not hours_str else ''

    return f'{days_str}{hours_str}{minutes_str}{seconds_str}'


@register.filter
def duration_short(td):
    s = duration(td)

    # replace day|days with d and so on
    s = s.replace(' days', 'd').replace(' day', 'd')
    s = s.replace(' hours', 'h').replace(' hour', 'h')
    s = s.replace(' minutes', 'm').replace(' minute', 'm')
    s = s.replace(' seconds', 's').replace(' second', 's')
    return s


# https://stackoverflow.com/a/35568978/4854605
@register.filter(name='range')
def _range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)
