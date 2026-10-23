from django.db import models
from profiles.models import Client, DigitalProfile

class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    registration_number = models.CharField(max_length=120, blank=True)
    services = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey(DigitalProfile, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company_name

class CompanyMember(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='members')
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.full_name
