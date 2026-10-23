from django.contrib import admin
from .models import QRCodeRecord


@admin.register(QRCodeRecord)
class QRCodeRecordAdmin(admin.ModelAdmin):
    list_display = ('profile', 'image', 'created_at')
    search_fields = ('profile__display_name', 'profile__unique_id', 'profile__slug')
    list_select_related = ('profile',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
