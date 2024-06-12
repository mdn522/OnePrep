from django.db import models


class Program(models.Model):
    name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


