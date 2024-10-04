
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, OneToOneField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField

from users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Digital SAT.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Full name"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)

    # username = None  # type: ignore[assignment]

    # TODO Organization system. multiple users
    # TODO User type: student, admin, parent, teacher, organization?, staff
    # TODO coin system
    # TODO referral system
    # TODO Transactions
    # TODO buy coin

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # TODO Profile picture
    # TODO bio
    # TODO social media links
    # TODO website
    # TODO location
    # TODO phone number
    # TODO date of birth
    # TODO timezone
    timezone = TimeZoneField(choices_display="WITH_GMT_OFFSET", default='UTC', blank=True)
    theme = models.CharField(max_length=255, default="light")
    notes = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True, default='', max_length=240)

    disable_donation_notice = models.BooleanField(default=False, blank=True, verbose_name="Disable Donation Notice")
    disable_donation_notice_until = models.DateTimeField(blank=True, null=True, verbose_name="Disable Donation Notice Until")
    has_donated = models.BooleanField(default=False, blank=True, verbose_name="Has Donated?")
    last_donated_at = models.DateTimeField(blank=True, null=True, verbose_name="Last Donated At")
    last_donation_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0, verbose_name="Last Donation Amount")
    last_donation_currency = models.CharField(max_length=3, blank=True, null=True, verbose_name="Last Donation Currency")
