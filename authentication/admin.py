from django.contrib import admin
from .models import User


@admin.register(User)
class User(admin.ModelAdmin):
    "Change the way users are displayed on the admin page"

    list_display = (
        'username',
        'email',
        'is_active',
        'can_be_contacted_display',
        'can_data_be_shared_display',
        'is_staff',
    )
    list_filter = (
        'is_active',
    )
    list_display_links = (
        'username',
    )
    search_fields = ('username', 'email')

    @admin.display(description='Contact ?', boolean=True)
    def can_be_contacted_display(self, obj):
        return obj.can_be_contacted

    @admin.display(description='Donnée partagée ?', boolean=True)
    def can_data_be_shared_display(self, obj):
        return obj.can_data_be_shared
