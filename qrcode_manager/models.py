from django.db import models
from django.utils import timezone
from profiles.models import DigitalProfile

class QRCodeRecord(models.Model):
    profile = models.ForeignKey(DigitalProfile, on_delete=models.CASCADE, related_name='qr_codes')
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'QR for {self.profile.display_name}'
