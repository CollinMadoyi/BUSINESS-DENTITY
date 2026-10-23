from django.contrib import admin
from .models import Client, DigitalProfile


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'client_type', 'organization', 'email', 'created_at')
    list_filter = ('client_type', 'organization', 'created_at')
    search_fields = (
        'display_name',
        'first_name',
        'last_name',
        'email',
        'phone',
        'unique_client_id',
        'external_reference',
    )
    readonly_fields = ('unique_client_id', 'created_at', 'updated_at')
    list_select_related = ('organization',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fieldsets = (
        ('Client details', {
            'fields': ('first_name', 'last_name', 'display_name', 'client_type'),
        }),
        ('Contact information', {
            'fields': ('email', 'phone', 'address', 'profile_photo', 'organization'),
        }),
        ('References and audit', {
            'fields': ('unique_client_id', 'external_reference', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(DigitalProfile)
class DigitalProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'profile_type', 'organization', 'unique_id', 'is_active', 'created_at')
    list_filter = ('profile_type', 'is_active', 'organization', 'created_at')
    search_fields = (
        'display_name',
        'first_name',
        'last_name',
        'unique_id',
        'slug',
        'email',
        'phone',
        'client__display_name',
        'organization__name',
    )
    readonly_fields = ('public_id', 'qr_code_url', 'created_at', 'updated_at')
    list_select_related = ('client', 'organization')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 50
    fieldsets = (
        ('Identity', {
            'fields': ('client', 'profile_type', 'first_name', 'last_name', 'display_name', 'title', 'department'),
        }),
        ('Organization and contact', {
            'fields': ('organization', 'phone', 'email', 'website', 'address', 'google_maps_url'),
        }),
        ('Profile content', {
            'fields': ('bio', 'profile_photo', 'about_video', 'organization_logo', 'color_theme'),
        }),
        ('Social links', {
            'fields': ('linkedin_url', 'whatsapp_number', 'social_links'),
            'classes': ('collapse',),
        }),
        ('Public access and QR code', {
            'fields': ('is_active', 'slug', 'public_id', 'unique_id', 'qr_code', 'qr_code_url'),
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
