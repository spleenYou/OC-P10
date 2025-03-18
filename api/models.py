from django.conf import settings
from django.db import models


class Contributors(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    projects = models.ManyToManyField(
        'Project',
        related_name='contributors',
    )

    def __str__(self):
        return f"{self.user.username} - Contributors"


class Project(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Auteur',
        related_name='Projects_created',
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Titre',
    )
    description = models.TextField()
    type = models.CharFiel(
        max_length=20,
        choices=[
            ('back-end', 'back-end'),
            ('front-end', 'front-end'),
            ('iOS', 'iOS'),
            ('Android', 'Android'),
        ]
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    def __str__(self):
        return self.title


class Issue(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Auteur',
        related_name='issues_created',
    )
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        verbose_name='Projet',
        related_name='issues'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Titre'
    )
    description = models.TextField()
    status = models.CharFiel(
        max_length=10,
        choices=[
            ('To-Do', 'To-Do'),
            ('In Progress', 'In Progress'),
            ('Finished', 'Finished'),
        ],
        default='To-Do',
    )
    priority = models.CharFiel(
        max_length=6,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
        ],
        default='LOW',
    )
    tag = models.CharFiel(
        max_length=12,
        choices=[
            ('BUG', 'Bug'),
            ('TASK', 'Task'),
            ('FEATURE', 'Feature'),
        ],
    )
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Utilisateur affecté',
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création',
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Auteur',
        related_name='comments_created',
    )
    issue = models.ForeignKey(
        'Issue',
        on_delete=models.CASCADE,
        verbose_name='Problème',
        related_name='comments',
    )
    description = models.TextField()
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création',
    )

    def __str__(self):
        return f"Commentaire pour {self.issue.title} by {self.author.username}"
