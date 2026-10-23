from django.db import models
from profiles.models import Client, DigitalProfile

class StudentRecord(models.Model):
    student_number = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=200)
    programme = models.CharField(max_length=200, blank=True)
    faculty = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    university = models.CharField(max_length=200, blank=True)
    academic_year = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey(DigitalProfile, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
