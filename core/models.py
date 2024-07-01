from django.db import models


from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase


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
