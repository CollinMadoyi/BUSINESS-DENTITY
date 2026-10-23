from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'website', 'updated_at')
    search_fields = ('name', 'email', 'phone', 'website', 'address')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    fieldsets = (
        ('Organization details', {
            'fields': ('name', 'logo', 'description', 'website'),
        }),
        ('Contact information', {
            'fields': ('email', 'phone', 'address'),
        }),
        ('Social links', {
            'fields': ('social_links',),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
