from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):

    birthday = models.DateField(null=False, blank=False, default=datetime.today().strftime("%Y-%m-%d"))
    can_be_contacted = models.BooleanField(null=False, blank=False, default=False)
    can_data_be_shared = models.BooleanField(null=False, blank=False, default=False)

    REQUIRED_FIELDS = ['birthday', 'can_be_contacted', 'can_data_be_shared']

    class Meta:
        verbose_name = 'Liste d\'utilisateur'
        verbose_name_plural = 'Liste des utilisateurs'
