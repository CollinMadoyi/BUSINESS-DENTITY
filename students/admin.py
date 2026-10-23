from django.contrib import admin
from .models import StudentRecord


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ('student_number', 'name', 'programme', 'university', 'academic_year', 'email')
    search_fields = ('student_number', 'name', 'email', 'programme', 'faculty', 'department', 'university')
    list_filter = ('university', 'faculty', 'academic_year')
    list_select_related = ('client', 'profile')
    ordering = ('name',)
    fieldsets = (
        ('Student details', {
            'fields': ('student_number', 'name', 'programme', 'faculty', 'department', 'academic_year'),
        }),
        ('Contact and linked records', {
            'fields': ('university', 'email', 'phone', 'client', 'profile'),
        }),
    )
