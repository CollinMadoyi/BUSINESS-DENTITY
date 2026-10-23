from django.contrib import admin
from .models import ContactRecord


@admin.register(ContactRecord)
class ContactRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'profile', 'created_at')
    search_fields = ('name', 'email', 'phone', 'profile__display_name')
    list_filter = ('created_at',)
    list_select_related = ('profile',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
