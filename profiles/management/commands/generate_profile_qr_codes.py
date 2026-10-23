from django.core.management.base import BaseCommand, CommandError
from profiles.models import (
    GENERATED_QR_PREFIX,
    DigitalProfile,
    configured_site_url,
    qr_profile_url,
)


class Command(BaseCommand):
    help = 'Generate QR codes for profiles that do not have one.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate-generated',
            action='store_true',
            help='Regenerate application-generated QR codes for the current profile URLs.',
        )

    def handle(self, *args, **options):
        if not configured_site_url():
            raise CommandError(
                'SITE_URL must be a valid absolute HTTP(S) base URL without credentials, query, or fragment '
                'before generating profile QR codes.'
            )

        profiles = DigitalProfile.objects.all().iterator(chunk_size=500)
        generated = 0
        for profile in profiles:
            qr_name = profile.qr_code.name if profile.qr_code else ''
            is_generated_qr = qr_name.startswith(GENERATED_QR_PREFIX)
            target_url = qr_profile_url(profile)
            if not target_url:
                raise CommandError(
                    f'Could not build a valid public URL for profile {profile.pk}; no QR codes were generated for it.'
                )
            if qr_name and not is_generated_qr:
                continue
            if (
                is_generated_qr
                and not options['regenerate_generated']
                and profile.qr_code_url == target_url
                and profile.qr_code.storage.exists(qr_name)
            ):
                continue
            if options['regenerate_generated'] and is_generated_qr:
                profile.qr_code_url = ''

            profile.save()
            if profile.qr_code and profile.qr_code.storage.exists(profile.qr_code.name):
                generated += 1

        self.stdout.write(self.style.SUCCESS(f'Generated QR codes for {generated} profile(s).'))