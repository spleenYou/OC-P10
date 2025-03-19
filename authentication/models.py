from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):

    birthday = models.DateField(
        null=False,
        blank=False,
        default=datetime.today().strftime("%Y-%m-%d")
    )
    can_be_contacted = models.BooleanField(blank=False, null=False)
    can_data_be_shared = models.BooleanField(blank=False, null=False)

    REQUIRED_FIELDS = ['birthday', 'can_be_contacted', 'can_data_be_shared']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Liste d\'utilisateur'
        verbose_name_plural = 'Liste des utilisateurs'
