from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    birthday = models.DateTimeField()
    can_be_contacted = models.BooleanField()
    can_data_be_shared = models.BooleanField()

    class Meta:
        verbose_name = 'Liste d\'utilisateur'
        verbose_name_plural = 'Liste des utilisateurs'
