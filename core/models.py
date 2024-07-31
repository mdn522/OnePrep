from django.db import models
from django.db.models import Subquery, PositiveIntegerField

from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase


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
