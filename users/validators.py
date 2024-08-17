from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator


custom_username_validators = [
    MinLengthValidator(5),
    ASCIIUsernameValidator()
]
