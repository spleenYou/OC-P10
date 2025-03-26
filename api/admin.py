from django.contrib import admin
from api.models import Contributors, Issue, Project, Comment


@admin.register(Contributors)
class ContributorsAdmin(admin.ModelAdmin):
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


class ContributorsInline(admin.TabularInline):
    model = Contributors
    fields = ('user',)
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ContributorsInline]
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
class IssueAdmin(admin.ModelAdmin):
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
