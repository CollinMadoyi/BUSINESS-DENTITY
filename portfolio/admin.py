from django.contrib import admin
from .models import PortfolioProfile, PortfolioProject


@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
    list_display = ('client',)
    search_fields = ('client__display_name', 'client__email')
    list_select_related = ('client',)


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'portfolio', 'project_url', 'github_url')
    search_fields = ('title', 'technologies', 'portfolio__client__display_name')
    list_select_related = ('portfolio', 'portfolio__client')
    ordering = ('title',)
