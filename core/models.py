import importlib

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Subquery, PositiveIntegerField
from django_login_history2.models import Login

from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django_login_history2.app_settings import (GEOLOCATION_METHOD, GEOLOCATION_BLOCK_FIELDS,
                           GEOLOCATION_PLACEHOLDER_IP)
from ipware import get_client_ip
from django_login_history2.utils import get_geolocation_data
from django.contrib.auth.signals import user_logged_in

from users.models import User


class SubqueryCount(Subquery):
    # Custom Count function to just perform simple count on any queryset without grouping.
    # https://gist.github.com/bblanchon/9e158058fe360e93b1c5d5ce5310015e
    # https://stackoverflow.com/a/47371514/1164966
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = PositiveIntegerField()


class SubqueryAggregate(Subquery):
    # https://code.djangoproject.com/ticket/10060
    template = '(SELECT %(function)s(_agg."%(column)s") FROM (%(subquery)s) _agg)'

    def __init__(self, queryset, column, output_field=None, **extra):
        if not output_field:
            # infer output_field from field type
            output_field = queryset.model._meta.get_field(column)
        super().__init__(queryset, output_field, column=column, function=self.function, **extra)


class SubquerySum(SubqueryAggregate):
    function = 'SUM'


class SkillTag(TagBase):
    class Meta:
        verbose_name = "Skill Tag"
        verbose_name_plural = "Skill Tags"


class SkillTagged(GenericTaggedItemBase):
    # TaggedWhatever can also extend TaggedItemBase or a combination of
    # both TaggedItemBase and GenericTaggedItemBase. GenericTaggedItemBase
    # allows using the same tag for different kinds of objects, in this
    # example Food and Drink.

    # Here is where you provide your custom Tag class.
    tag = models.ForeignKey(
        SkillTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    client_ip, is_routable = get_client_ip(request)
    method_path = GEOLOCATION_METHOD
    result = None
    mapped_fields = {}

    if not client_ip:
        client_ip = GEOLOCATION_PLACEHOLDER_IP

    else:
        if not is_routable:
            result = {"error": True, "reason": "Address not routable"}

        elif method_path:
            module_name, func_name = method_path.rsplit('.', 1)
            try:
                module = importlib.import_module(module_name)
                geolocation_func = getattr(module, func_name)
                result = geolocation_func(client_ip)
            except (ImportError, AttributeError) as er:
                raise ValueError("Invalid geolocation method specified in settings.\n", er) from er

    if not result:
        result = get_geolocation_data(client_ip)
        assert isinstance(result, dict)

        for key, value in result.items():

            if key in GEOLOCATION_BLOCK_FIELDS:
                continue

            try:
                _ = Login._meta.get_field(key)
                mapped_fields[key] = value or ''
            except FieldDoesNotExist:
                pass

    _ = Login.objects.create(
        user=user,
        ip=client_ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ip_info=result,
        **mapped_fields
    )

for x in user_logged_in._live_receivers(User)[0]:
    if str(x.__module__).startswith('django_login_history2'):
        user_logged_in.disconnect(x)
