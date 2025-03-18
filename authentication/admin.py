from django.contrib import admin
from .models import User


@admin.register(User)
class User(admin.ModelAdmin):
    "Change the way users are displayed on the admin page"

    list_display = (
        'username',
        'email',
        'is_active',
        'is_staff',
    )
    list_filter = (
        'is_active',
    )
    list_display_links = (
        'username',
    )
    search_fields = ('username', 'email')
