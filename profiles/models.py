import logging
import uuid
from io import BytesIO
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
import qrcode
from organizations.models import Organization
from accounts.models import CustomUser


def create_client_reference():
    return str(uuid.uuid4())[:12]


def create_profile_reference():
    return uuid.uuid4().hex[:12]


MAX_ABOUT_VIDEO_SIZE = 50 * 1024 * 1024
GENERATED_QR_PREFIX = 'qr_codes/generated/'
logger = logging.getLogger(__name__)


def public_profile_path(profile):
    route_names = {
        'BUSINESS_ID': 'business_profile',
        'STUDENT_ID': 'student_profile',
        'PORTFOLIO_ID': 'portfolio_profile',
        'COMPANY_ID': 'company_profile',
    }
    route_name = route_names.get(profile.profile_type, 'public_profile')
    return reverse(route_name, kwargs={'slug': profile.slug})


def public_profile_url(profile):
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url:
        return None
    return f'{site_url}{public_profile_path(profile)}'


def configured_site_url():
    site_url = getattr(settings, 'SITE_URL', '').strip()
    if not site_url or any(character.isspace() for character in site_url):
        return None
    try:
        parsed_url = urlsplit(site_url)
        port = parsed_url.port
    except ValueError:
        return None
    if (
        parsed_url.scheme not in {'http', 'https'}
        or not parsed_url.hostname
        or parsed_url.username
        or parsed_url.password
        or parsed_url.query
        or parsed_url.fragment
    ):
        return None
    if port is not None and not 1 <= port <= 65535:
        return None
    return site_url.rstrip('/')


def qr_profile_url(profile):
    site_url = configured_site_url()
    if not site_url:
        return None
    path = reverse('profile_by_public_id', kwargs={'public_id': profile.public_id})
    return f'{site_url}{path}'


def validate_about_video_size(upload):
    if upload.size > MAX_ABOUT_VIDEO_SIZE:
        raise ValidationError('Video files must be 50 MB or smaller.')


class Client(models.Model):
    class ClientType(models.TextChoices):
        BUSINESS_CLIENT = 'BUSINESS_CLIENT', 'Business Client'
        STUDENT = 'STUDENT', 'Student'
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        PROFESSIONAL = 'PROFESSIONAL', 'Professional'
        COMPANY_REPRESENTATIVE = 'COMPANY_REPRESENTATIVE', 'Company Representative'
        OTHER = 'OTHER', 'Other'

    unique_client_id = models.CharField(max_length=80, unique=True, default=create_client_reference)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    client_type = models.CharField(max_length=30, choices=ClientType.choices, default=ClientType.OTHER)
    external_reference = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='created_clients', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='updated_clients', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f'{self.first_name} {self.last_name}'.strip()
        super().save(*args, **kwargs)

class DigitalProfile(models.Model):
    class ProfileType(models.TextChoices):
        BUSINESS_ID = 'BUSINESS_ID', 'Business ID'
        PORTFOLIO_ID = 'PORTFOLIO_ID', 'Portfolio ID'
        STUDENT_ID = 'STUDENT_ID', 'Student ID'
        COMPANY_ID = 'COMPANY_ID', 'Company ID'
        STAFF_ID = 'STAFF_ID', 'Staff ID'
        PROFESSIONAL_ID = 'PROFESSIONAL_ID', 'Professional ID'

    class ColorTheme(models.TextChoices):
        OCEAN = 'OCEAN', 'Ocean'
        SUNSET = 'SUNSET', 'Sunset'
        FOREST = 'FOREST', 'Forest'
        ROYAL = 'ROYAL', 'Royal'
        LAVENDER = 'LAVENDER', 'Lavender'
        ROSE = 'ROSE', 'Rose'
        SLATE = 'SLATE', 'Slate'
        SAND = 'SAND', 'Sand'

    unique_id = models.CharField(max_length=80, unique=True, default=create_profile_reference)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='profiles')
    profile_type = models.CharField(max_length=30, choices=ProfileType.choices, default=ProfileType.BUSINESS_ID)
    color_theme = models.CharField(
        max_length=10,
        choices=ColorTheme.choices,
        default=ColorTheme.FOREST,
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    display_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    about_video = models.FileField(
        upload_to='profile_videos/',
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogv']),
            validate_about_video_size,
        ],
    )
    organization_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True)
    google_maps_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Google Maps location URL',
    )
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_code_url = models.URLField(max_length=500, blank=True, editable=False)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='created_profiles', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='updated_profiles', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f'{self.first_name}-{self.last_name}'.lower()
            self.slug = base
            counter = 2
            while DigitalProfile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{base}-{counter}'
                counter += 1
        if not self.display_name:
            self.display_name = f'{self.first_name} {self.last_name}'.strip()
        super().save(*args, **kwargs)

        qr_name = self.qr_code.name or ''
        is_generated_qr = qr_name.startswith(GENERATED_QR_PREFIX)
        if qr_name and not is_generated_qr:
            if self.qr_code_url:
                self.qr_code_url = ''
                type(self).objects.filter(pk=self.pk).update(qr_code_url='')
            return

        target_url = qr_profile_url(self)
        if not target_url:
            logger.warning(
                'QR code was not generated or refreshed for profile %s because SITE_URL is missing or invalid. '
                'Set SITE_URL to an absolute HTTP(S) base URL and run '
                '"python manage.py generate_profile_qr_codes" to backfill it.',
                self.pk,
            )
            return

        if (
            is_generated_qr
            and self.qr_code_url == target_url
            and self.qr_code.storage.exists(qr_name)
        ):
            return

        image = qrcode.make(target_url)
        image_buffer = BytesIO()
        image.save(image_buffer, format='PNG')
        old_qr_name = qr_name if is_generated_qr else ''
        self.qr_code.save(
            f'generated/profile-{self.pk}.png',
            ContentFile(image_buffer.getvalue()),
            save=False,
        )
        type(self).objects.filter(pk=self.pk).update(
            qr_code=self.qr_code.name,
            qr_code_url=target_url,
        )
        self.qr_code_url = target_url
        if old_qr_name and old_qr_name != self.qr_code.name:
            self.qr_code.storage.delete(old_qr_name)
