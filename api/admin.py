from django.contrib import admin
from api.models import Contributors, Issue, Project, Comment


@admin.register(Contributors)
class Contributors(admin.ModelAdmin):
    fields = (
        'user',
        'project'
    )
    list_display = (
        'user',
        'project',
    )
    list_filter = (
        'user',
        'project',
    )


@admin.register(Project)
class Project(admin.ModelAdmin):
    fields = (
        'author',
        'title',
        'description',
        'project_type',
    )
    list_display = (
        'title',
        'author',
        'project_type',
    )
    list_filter = (
        'author',
        'project_type',
        'date_created',
    )


@admin.register(Issue)
class Issue(admin.ModelAdmin):
    list_display = (
        'author',
        'project',
        'title',
        'description',
        'priority',
        'status',
        'tag',
        'assigned_user',
    )

    list_filter = (
        'author',
        'project',
        'priority',
        'status',
        'tag',
        'assigned_user',
    )


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = (
        'author',
        'issue',
    )
