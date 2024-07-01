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

