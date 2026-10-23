import tempfile
from io import BytesIO, StringIO
from unittest.mock import patch
import qrcode
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from urllib.parse import parse_qs, urlsplit
from PIL import Image
from organizations.models import Organization
from .forms import BusinessProfileForm
from .models import MAX_ABOUT_VIDEO_SIZE, Client, DigitalProfile, validate_about_video_size


class BusinessProfileViewTests(TestCase):
	def setUp(self):
		self.media_directory = tempfile.TemporaryDirectory()
		self.addCleanup(self.media_directory.cleanup)
		self.media_override = override_settings(MEDIA_ROOT=self.media_directory.name)
		self.media_override.enable()
		self.addCleanup(self.media_override.disable)
		self.site_override = override_settings(SITE_URL='https://identity.example')
		self.site_override.enable()
		self.addCleanup(self.site_override.disable)
		self.organization = Organization.objects.create(
			name='Northstar Studio',
			email='hello@northstar.example',
			social_links={'Instagram': 'https://instagram.com/northstar'},
		)
		self.client_record = Client.objects.create(
			first_name='Alex',
			last_name='Rivera',
		)

	def create_profile(self, **overrides):
		values = {
			'client': self.client_record,
			'profile_type': DigitalProfile.ProfileType.BUSINESS_ID,
			'first_name': 'Alex',
			'last_name': 'Rivera',
			'display_name': 'Alex Rivera',
			'slug': 'alex-rivera',
			'organization': self.organization,
			'email': 'alex@example.com',
			'phone': '+256700123456',
			'linkedin_url': 'https://linkedin.com/in/alex',
			'whatsapp_number': '+256700123456',
			'is_active': True,
		}
		values.update(overrides)
		return DigitalProfile.objects.create(**values)

	def test_business_route_renders_standalone_business_experience(self):
		self.create_profile()

		response = self.client.get(reverse('business_profile', args=['alex-rivera']))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'profile.html')
		self.assertContains(response, 'Northstar Studio')
		self.assertContains(response, 'hello@northstar.example')
		self.assertContains(response, 'Instagram')
		self.assertContains(response, 'Social profiles')
		self.assertContains(response, 'href="https://linkedin.com/in/alex"')
		self.assertContains(response, 'href="https://wa.me/256700123456"')
		self.assertContains(response, 'href="https://instagram.com/northstar"')
		self.assertContains(response, 'Save contact')
		self.assertContains(response, 'href="/api/public/profile/alex-rivera/vcard/"')
		self.assertContains(response, 'Copy link')
		self.assertContains(response, 'Share on WhatsApp')
		self.assertContains(response, 'property="og:title" content="Alex Rivera | Digital Profile"')
		self.assertContains(response, 'property="og:description"')
		self.assertContains(response, 'property="og:image" content="https://identity.example/card/alex-rivera/share.png"')
		self.assertContains(response, 'property="og:url" content="https://identity.example/business/alex-rivera/"')
		self.assertContains(response, 'property="og:type" content="profile"')
		self.assertContains(response, 'name="twitter:card" content="summary_large_image"')
		self.assertContains(response, 'name="twitter:image" content="https://identity.example/card/alex-rivera/share.png"')
		share_link = response.context['whatsapp_share_url']
		share_text = parse_qs(urlsplit(share_link).query)['text'][0]
		self.assertIn('Alex Rivera', share_text)
		self.assertIn('https://identity.example/business/alex-rivera/', share_text)
		self.assertNotContains(response, 'dashboard-shell')
		self.assertNotContains(response, 'Admin Panel')

	def test_profile_theme_defaults_to_forest_and_is_applied_to_public_page_and_api(self):
		profile = self.create_profile(color_theme=DigitalProfile.ColorTheme.OCEAN)

		response = self.client.get(reverse('public_profile', args=[profile.slug]))
		api_response = self.client.get(reverse('public_profile_api', args=[profile.slug]))

		self.assertContains(response, 'profile-color-theme-ocean')
		self.assertEqual(api_response.json()['color_theme'], DigitalProfile.ColorTheme.OCEAN)
		default_profile = self.create_profile(slug='forest-profile')
		self.assertEqual(default_profile.color_theme, DigitalProfile.ColorTheme.FOREST)

	def test_added_background_themes_are_saved_and_applied_to_public_pages(self):
		profile = self.create_profile(color_theme=DigitalProfile.ColorTheme.LAVENDER)

		response = self.client.get(reverse('public_profile', args=[profile.slug]))
		profile.refresh_from_db()

		self.assertEqual(profile.color_theme, DigitalProfile.ColorTheme.LAVENDER)
		self.assertContains(response, 'profile-color-theme-lavender')
		self.assertContains(response, 'profile-color-theme-rose')
		self.assertContains(response, 'profile-color-theme-slate')
		self.assertContains(response, 'profile-color-theme-sand')

	def test_profile_theme_form_rejects_unsupported_choices(self):
		with self.assertRaises(ValidationError):
			BusinessProfileForm().fields['color_theme'].clean('NEON')
		self.assertEqual(
			BusinessProfileForm().fields['color_theme'].clean('LAVENDER'),
			DigitalProfile.ColorTheme.LAVENDER,
		)

	def test_save_contact_downloads_phone_ready_vcard(self):
		profile = self.create_profile(
			display_name='Alex Rivera, Jr.',
			first_name='Alex',
			last_name='Rivera, Jr.',
			phone='+256700123456',
			email='alex@example.com',
			website='https://alex.example',
			address='Kampala; Uganda',
		)

		response = self.client.get(reverse('public_vcard', args=[profile.slug]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'text/vcard; charset=utf-8')
		self.assertIn('attachment; filename="alex-rivera.vcf"', response['Content-Disposition'])
		vcard = response.content.decode('utf-8')
		self.assertIn('BEGIN:VCARD\r\nVERSION:3.0\r\n', vcard)
		self.assertIn('FN:Alex Rivera\\, Jr.', vcard)
		self.assertIn('N:Rivera\\, Jr.;Alex;;;', vcard)
		self.assertIn('TEL;TYPE=CELL:+256700123456', vcard)
		self.assertIn('EMAIL:alex@example.com', vcard)
		self.assertIn('URL:https://alex.example', vcard)
		self.assertIn('ADR;TYPE=WORK:;;Kampala\\; Uganda;;;;', vcard)
		self.assertTrue(vcard.endswith('END:VCARD\r\n'))

	def test_printable_card_download_has_expected_pdf_metadata_and_profile_content(self):
		profile = self.create_profile(
			title='Software Engineer',
			department='Marketing',
			unique_id='BIZ-8421',
			phone='+256700123456',
			email='alex@example.com',
			website='https://alex.example',
			address='Kampala, Uganda',
		)
		url = reverse('download_profile_card', args=[profile.slug])

		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'application/pdf')
		self.assertIn('attachment; filename="alex-rivera-printable-card.pdf"', response['Content-Disposition'])
		pdf = b''.join(response.streaming_content)
		self.assertTrue(pdf.startswith(b'%PDF-'))
		self.assertIn(b'/MediaBox [ 0 0 252 144 ]', pdf)
		self.assertIn(b'Alex Rivera', pdf)
		self.assertIn(b'Software Engineer', pdf)
		self.assertIn(b'Northstar Studio', pdf)
		self.assertIn(b'BIZ-8421', pdf)
		self.assertIn(b'Marketing', pdf)
		self.assertIn(b'+256700123456', pdf)
		self.assertIn(b'alex@example.com', pdf)
		self.assertIn(b'https://alex.example', pdf)
		self.assertIn(b'Kampala, Uganda', pdf)
		self.assertIn(b'/Subtype /Image', pdf)

	def test_printable_card_download_includes_available_profile_and_organization_images(self):
		def png_upload(name, color):
			image_data = BytesIO()
			Image.new('RGB', (12, 12), color).save(image_data, format='PNG')
			return SimpleUploadedFile(name, image_data.getvalue(), content_type='image/png')

		self.organization.logo = png_upload('organization.png', 'blue')
		self.organization.save()
		profile = self.create_profile(
			profile_photo=png_upload('profile.png', 'green'),
		)
		response = self.client.get(reverse('download_profile_card', args=[profile.slug]))
		pdf = b''.join(response.streaming_content)

		self.assertGreaterEqual(pdf.count(b'/Subtype /Image'), 3)

	def test_printable_card_omits_missing_qr_image_cleanly(self):
		with override_settings(SITE_URL=''):
			profile = self.create_profile()
		response = self.client.get(reverse('download_profile_card', args=[profile.slug]))
		pdf = b''.join(response.streaming_content)

		self.assertEqual(pdf.count(b'/Subtype /Image'), 0)

	def test_printable_card_download_hides_inactive_profiles(self):
		profile = self.create_profile(is_active=False)

		response = self.client.get(reverse('download_profile_card', args=[profile.slug]))

		self.assertEqual(response.status_code, 404)

	def test_share_image_is_a_1200_by_630_png_and_reuses_profile_qr(self):
		profile = self.create_profile()
		response = self.client.get(reverse('profile_share_image', args=[profile.slug]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'image/png')
		self.assertEqual(response['Cache-Control'], 'no-store')
		with Image.open(BytesIO(response.content)) as image:
			self.assertEqual(image.format, 'PNG')
			self.assertEqual(image.size, (1200, 630))
			qr_region = image.crop((934, 375, 1128, 569)).convert('RGB')
			self.assertGreater(len(qr_region.getcolors(maxcolors=1_000_000)), 1)

	def test_share_image_hides_inactive_profiles(self):
		profile = self.create_profile(is_active=False)

		response = self.client.get(reverse('profile_share_image', args=[profile.slug]))

		self.assertEqual(response.status_code, 404)

	def test_new_profile_generates_png_qr_for_its_public_url(self):
		with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
			profile = self.create_profile()

		public_url = f'https://identity.example/item/{profile.public_id}/'
		make_qr.assert_called_once_with(public_url)
		self.assertTrue(profile.qr_code.name.startswith('qr_codes/generated/'))
		self.assertEqual(profile.qr_code_url, public_url)
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))
		with Image.open(profile.qr_code.path) as image:
			self.assertEqual(image.format, 'PNG')

		response = self.client.get(reverse('profile_by_public_id', args=[profile.public_id]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Alex Rivera')

		response = self.client.get(reverse('public_profile', args=[profile.slug]))
		self.assertContains(response, f'src="{profile.qr_code.url}"')

		staff_user = get_user_model().objects.create_user(
			username='qr-download-staff',
			email='qr-download-staff@example.com',
			password='test-password',
			is_staff=True,
		)
		self.client.force_login(staff_user)
		response = self.client.get(reverse('dashboard_home'))
		self.assertContains(response, f'href="{profile.qr_code.url}" download')

	def test_qr_generation_uses_the_profile_type_public_route(self):
		profile_types = [
			DigitalProfile.ProfileType.BUSINESS_ID,
			DigitalProfile.ProfileType.PORTFOLIO_ID,
			DigitalProfile.ProfileType.STUDENT_ID,
			DigitalProfile.ProfileType.COMPANY_ID,
			DigitalProfile.ProfileType.STAFF_ID,
			DigitalProfile.ProfileType.PROFESSIONAL_ID,
		]
		for profile_type in profile_types:
			with self.subTest(profile_type=profile_type):
				with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
					profile = self.create_profile(
						slug=f'{profile_type.lower().replace("_id", "")}-card',
						profile_type=profile_type,
					)
				make_qr.assert_called_once_with(
					f'https://identity.example/item/{profile.public_id}/'
				)

	def test_slug_change_preserves_generated_qr_public_url(self):
		profile = self.create_profile(profile_type=DigitalProfile.ProfileType.PORTFOLIO_ID)
		original_qr_name = profile.qr_code.name

		with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
			profile.slug = 'alex-rivera-updated'
			profile.save()

		make_qr.assert_not_called()
		self.assertEqual(profile.qr_code.name, original_qr_name)
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))

	def test_generated_qr_refreshes_when_configured_public_url_changes(self):
		profile = self.create_profile()
		old_qr_name = profile.qr_code.name

		with override_settings(SITE_URL='https://new-identity.example'):
			with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
				profile.save()

		new_url = f'https://new-identity.example/item/{profile.public_id}/'
		make_qr.assert_called_once_with(new_url)
		self.assertEqual(profile.qr_code_url, new_url)
		self.assertNotEqual(profile.qr_code.name, old_qr_name)
		self.assertFalse(profile.qr_code.storage.exists(old_qr_name))
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))

	def test_generated_qr_is_restored_when_its_saved_file_is_missing(self):
		profile = self.create_profile()
		qr_name = profile.qr_code.name
		profile.qr_code.storage.delete(qr_name)

		with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
			profile.save()

		make_qr.assert_called_once_with(profile.qr_code_url)
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))

	def test_slug_change_without_site_url_keeps_generated_uuid_qr_valid(self):
		profile = self.create_profile()
		old_qr_name = profile.qr_code.name

		with override_settings(SITE_URL=''):
			with patch('profiles.models.qrcode.make', wraps=qrcode.make) as make_qr:
				profile.slug = 'alex-rivera-updated'
				profile.save()

		profile.refresh_from_db()
		make_qr.assert_not_called()
		self.assertEqual(profile.qr_code.name, old_qr_name)
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))

	def test_regenerate_command_updates_generated_qrs_but_keeps_manual_uploads(self):
		generated_profile = self.create_profile()
		old_generated_name = generated_profile.qr_code.name
		manual_profile = self.create_profile(
			slug='manual-qr',
			qr_code=SimpleUploadedFile('manual.png', b'manual-qr-image', content_type='image/png'),
		)
		manual_name = manual_profile.qr_code.name

		call_command('generate_profile_qr_codes', '--regenerate-generated')

		generated_profile.refresh_from_db()
		manual_profile.refresh_from_db()
		self.assertNotEqual(generated_profile.qr_code.name, old_generated_name)
		self.assertFalse(generated_profile.qr_code.storage.exists(old_generated_name))
		self.assertEqual(manual_profile.qr_code.name, manual_name)
		with manual_profile.qr_code.open('rb') as qr_file:
			self.assertEqual(qr_file.read(), b'manual-qr-image')

	def test_uuid_profile_url_hides_inactive_and_unknown_profiles(self):
		profile = self.create_profile()
		url = reverse('profile_by_public_id', args=[profile.public_id])

		self.assertEqual(self.client.get(url).status_code, 200)
		profile.is_active = False
		profile.save()
		self.assertEqual(self.client.get(url).status_code, 404)
		self.assertEqual(
			self.client.get(reverse('profile_by_public_id', args=['00000000-0000-0000-0000-000000000001'])).status_code,
			404,
		)

	def test_manual_qr_upload_is_not_overwritten_on_slug_change(self):
		profile = self.create_profile(
			qr_code=SimpleUploadedFile('custom.png', b'manual-qr-image', content_type='image/png')
		)
		original_name = profile.qr_code.name

		profile.slug = 'alex-rivera-updated'
		profile.save()

		self.assertEqual(profile.qr_code.name, original_name)
		self.assertEqual(profile.qr_code_url, '')
		with profile.qr_code.open('rb') as qr_file:
			self.assertEqual(qr_file.read(), b'manual-qr-image')

	def test_invalid_site_url_does_not_generate_qr(self):
		with override_settings(SITE_URL='javascript:alert(1)'):
			with self.assertLogs('profiles.models', level='WARNING') as log_output:
				profile = self.create_profile()

		self.assertFalse(profile.qr_code)
		self.assertIn('missing or invalid', log_output.output[0])

	def test_backfill_command_requires_a_valid_site_url(self):
		for site_url in ('', 'javascript:alert(1)', 'https://example.com/?next=other'):
			with self.subTest(site_url=site_url), override_settings(SITE_URL=site_url):
				with self.assertRaisesMessage(CommandError, 'SITE_URL must be a valid absolute HTTP(S) base URL'):
					call_command('generate_profile_qr_codes')

	def test_management_command_backfills_profiles_without_qr_codes(self):
		with override_settings(SITE_URL=''):
			with self.assertLogs('profiles.models', level='WARNING') as log_output:
				profile = self.create_profile()
		self.assertFalse(profile.qr_code)
		self.assertIn('SITE_URL', log_output.output[0])

		command_output = StringIO()
		call_command('generate_profile_qr_codes', stdout=command_output)

		profile.refresh_from_db()
		self.assertTrue(profile.qr_code.name.startswith('qr_codes/generated/'))
		self.assertEqual(
			profile.qr_code_url,
			f'https://identity.example/item/{profile.public_id}/',
		)
		self.assertTrue(profile.qr_code.storage.exists(profile.qr_code.name))
		self.assertEqual(command_output.getvalue(), 'Generated QR codes for 1 profile(s).\n')

	def test_profile_owner_only_displays_social_profiles_with_saved_urls(self):
		owner = get_user_model().objects.create_user(
			username='social-owner', email='social@example.com', password='test-password'
		)
		self.organization.social_links = {}
		self.organization.save()
		profile = self.create_profile(created_by=owner, linkedin_url='', whatsapp_number='')
		self.client.force_login(owner)
		form_data = {
			'unique_id': profile.unique_id,
			'slug': profile.slug,
			'first_name': profile.first_name,
			'last_name': profile.last_name,
			'display_name': profile.display_name,
			'color_theme': DigitalProfile.ColorTheme.ROYAL,
			'is_active': 'on',
			'social_instagram': 'https://instagram.com/alex',
		}

		response = self.client.post(reverse('edit_business_profile', args=[profile.slug]), form_data)

		self.assertRedirects(response, reverse('public_profile', args=[profile.slug]))
		profile.refresh_from_db()
		self.assertEqual(profile.social_links, {'Instagram': 'https://instagram.com/alex'})
		self.assertEqual(profile.color_theme, DigitalProfile.ColorTheme.ROYAL)
		response = self.client.get(reverse('public_profile', args=[profile.slug]))
		self.assertContains(response, 'href="https://instagram.com/alex"')
		self.assertContains(response, 'profile-color-theme-royal')
		self.assertNotContains(response, 'GitHub profile')
		self.assertNotContains(response, 'YouTube profile')

	def test_profile_owner_can_save_and_publish_google_maps_location(self):
		owner = get_user_model().objects.create_user(
			username='maps-owner', email='maps@example.com', password='test-password'
		)
		profile = self.create_profile(created_by=owner)
		self.client.force_login(owner)

		response = self.client.post(
			reverse('edit_business_profile', args=[profile.slug]),
			{
				'unique_id': profile.unique_id,
				'slug': profile.slug,
				'first_name': profile.first_name,
				'last_name': profile.last_name,
				'display_name': profile.display_name,
				'address': 'Kampala, Uganda',
				'google_maps_url': 'https://maps.google.com/?q=Kampala',
				'is_active': 'on',
			},
		)

		self.assertRedirects(response, reverse('public_profile', args=[profile.slug]))
		profile.refresh_from_db()
		self.assertEqual(profile.google_maps_url, 'https://maps.google.com/?q=Kampala')
		public_response = self.client.get(reverse('public_profile', args=[profile.slug]))
		self.assertContains(public_response, 'Kampala, Uganda')
		self.assertContains(public_response, 'href="https://maps.google.com/?q=Kampala"')
		self.assertContains(public_response, 'View on Google Maps')

		api_response = self.client.get(reverse('public_profile_api', args=[profile.slug]))
		self.assertEqual(api_response.json()['google_maps_url'], profile.google_maps_url)

	def test_business_route_hides_inactive_profiles(self):
		self.create_profile(is_active=False)

		response = self.client.get(reverse('business_profile', args=['alex-rivera']))

		self.assertEqual(response.status_code, 404)

	def test_business_route_rejects_non_business_profile_type(self):
		self.create_profile(profile_type=DigitalProfile.ProfileType.PORTFOLIO_ID)

		response = self.client.get(reverse('business_profile', args=['alex-rivera']))

		self.assertEqual(response.status_code, 404)

	def test_generic_public_route_still_serves_other_active_profiles(self):
		self.create_profile(profile_type=DigitalProfile.ProfileType.PORTFOLIO_ID)

		response = self.client.get(reverse('public_profile', args=['alex-rivera']))

		self.assertEqual(response.status_code, 200)

	def test_public_profile_shows_uploaded_video_with_controls(self):
		profile = self.create_profile(
			about_video=SimpleUploadedFile('intro.mp4', b'video-content', content_type='video/mp4')
		)

		response = self.client.get(reverse('public_profile', args=[profile.slug]))

		self.assertContains(response, 'About Me Video')
		self.assertContains(response, 'class="about-video" controls')
		self.assertContains(response, profile.about_video.url)

	def test_public_profile_hides_video_section_without_video(self):
		self.create_profile()

		response = self.client.get(reverse('public_profile', args=['alex-rivera']))

		self.assertNotContains(response, 'About Me Video')

	def test_profile_owner_can_upload_replace_and_remove_video(self):
		owner = get_user_model().objects.create_user(
			username='profile-owner', email='owner@example.com', password='test-password'
		)
		profile = self.create_profile(created_by=owner)
		self.client.force_login(owner)
		url = reverse('edit_business_profile', args=[profile.slug])
		form_data = {
			'unique_id': profile.unique_id,
			'slug': profile.slug,
			'first_name': profile.first_name,
			'last_name': profile.last_name,
			'display_name': profile.display_name,
			'is_active': 'on',
		}

		response = self.client.post(url, {
			**form_data,
			'about_video': SimpleUploadedFile('first.mp4', b'first-video', content_type='video/mp4'),
		})
		self.assertRedirects(response, reverse('public_profile', args=[profile.slug]))
		profile.refresh_from_db()
		self.assertEqual(profile.about_video.name, 'profile_videos/first.mp4')

		self.client.post(url, {
			**form_data,
			'about_video': SimpleUploadedFile('replacement.webm', b'new-video', content_type='video/webm'),
		})
		profile.refresh_from_db()
		self.assertEqual(profile.about_video.name, 'profile_videos/replacement.webm')

		self.client.post(url, {**form_data, 'about_video-clear': 'on'})
		profile.refresh_from_db()
		self.assertFalse(profile.about_video)

	def test_non_owner_cannot_edit_profile_video(self):
		owner = get_user_model().objects.create_user(
			username='profile-owner', email='owner@example.com', password='test-password'
		)
		other_user = get_user_model().objects.create_user(
			username='other-user', email='other@example.com', password='test-password'
		)
		profile = self.create_profile(created_by=owner)
		self.client.force_login(other_user)

		response = self.client.post(
			reverse('edit_business_profile', args=[profile.slug]),
			{'about_video': SimpleUploadedFile('intruder.mp4', b'video', content_type='video/mp4')},
		)

		self.assertEqual(response.status_code, 403)
		profile.refresh_from_db()
		self.assertFalse(profile.about_video)

	def test_about_video_rejects_disallowed_extension(self):
		video = SimpleUploadedFile('intro.exe', b'not-a-video')

		with self.assertRaises(ValidationError):
			BusinessProfileForm().fields['about_video'].clean(video)

	def test_about_video_rejects_files_over_size_limit(self):
		class OversizedUpload:
			size = MAX_ABOUT_VIDEO_SIZE + 1

		with self.assertRaises(ValidationError):
			validate_about_video_size(OversizedUpload())
