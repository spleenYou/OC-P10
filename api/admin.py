from django.contrib import admin
from api.models import Contributor, Issue, Project, Comment


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
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


class ContributorInline(admin.TabularInline):
    model = Contributor
    fields = ('user',)
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ContributorInline]
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
