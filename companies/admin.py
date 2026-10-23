from django.contrib import admin
from .models import CompanyMember, CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'registration_number', 'email', 'phone', 'website')
    search_fields = ('company_name', 'registration_number', 'email', 'phone', 'website')
    list_select_related = ('client', 'profile')
    ordering = ('company_name',)
    fieldsets = (
        ('Company details', {
            'fields': ('company_name', 'logo', 'registration_number', 'description', 'services'),
        }),
        ('Contact information', {
            'fields': ('website', 'email', 'phone', 'address'),
        }),
        ('Linked records', {'fields': ('client', 'profile')}),
    )


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'company', 'email', 'phone')
    search_fields = ('full_name', 'title', 'company__company_name', 'email', 'phone')
    list_filter = ('company',)
    list_select_related = ('company',)
    ordering = ('full_name',)
