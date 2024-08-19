
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, OneToOneField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # TODO Profile picture
#     # TODO bio
#     # TODO social media links
#     # TODO website
#     # TODO location
#     # TODO phone number
#     # TODO date of birth
#     # TODO timezone
#     theme = models.CharField(max_length=255, default="light")
