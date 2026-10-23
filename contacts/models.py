from django.db import models
from profiles.models import DigitalProfile

class ContactRecord(models.Model):
    profile = models.ForeignKey(DigitalProfile, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
