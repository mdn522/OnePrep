import functools
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
    return urlencode_f(value)
    # return urlencode(value)


def urlencode_f(args):
    e_args = []
    for k, v in args.items():
        if isinstance(v, list):
            for v1 in v:
                e_args.append(urlencode({k: v1}))
        elif v:
            e_args.append(urlencode({k: v}))

    return "&".join(e_args)



@register.filter
def merge_dict(dict1, dict2):
    return {**dict1, **dict2}


@register.filter
def get_dict_from_kv(k, v):
    return {k: v}

@register.filter
def append(lst, item):
    return lst + [item]

@register.filter
def prepend(lst, item):
    return [item] + lst

@register.filter
def remove(lst, item):
    return [x for x in lst if x != item]

@register.filter
def v_or_list(item):
    return item or []

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


# https://gist.github.com/MikaelSantilio/3e761b325c7fd7588207cec06fdcbefb
# https://cheat.readthedocs.io/en/latest/django/filter.html
# https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
