from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from organizations.models import Organization
from profiles.models import Client, DigitalProfile


class BusinessIdDashboardTests(TestCase):
	def setUp(self):
		self.staff_user = get_user_model().objects.create_user(
			username='staff',
			email='staff@example.com',
			password='test-password',
			is_staff=True,
		)
		self.organization = Organization.objects.create(name='Northstar Studio')
		self.client_record = Client.objects.create(first_name='Alex', last_name='Rivera')

	def create_profile(self, **overrides):
		values = {
			'client': self.client_record,
			'profile_type': DigitalProfile.ProfileType.BUSINESS_ID,
			'first_name': 'Alex',
			'last_name': 'Rivera',
			'display_name': 'Alex Rivera',
			'slug': 'alex-rivera',
			'unique_id': 'BIZ-1001',
			'organization': self.organization,
			'is_active': True,
		}
		values.update(overrides)
		return DigitalProfile.objects.create(**values)

	def test_dashboard_requires_staff_access(self):
		response = self.client.get(reverse('dashboard_home'))

		self.assertEqual(response.status_code, 302)

	def test_dashboard_lists_all_business_ids_with_matching_public_and_admin_actions(self):
		self.create_profile(qr_code='qr_codes/alex-rivera.png')
		self.create_profile(
			slug='inactive-business',
			unique_id='BIZ-1002',
			display_name='Inactive Business',
			is_active=False,
		)
		self.create_profile(
			slug='portfolio-entry',
			unique_id='PORT-1003',
			profile_type=DigitalProfile.ProfileType.PORTFOLIO_ID,
		)
		self.client.force_login(self.staff_user)

		response = self.client.get(reverse('dashboard_home'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Business IDs')
		self.assertContains(response, 'class="table-scroll"')
		self.assertContains(response, 'class="dashboard-table"')
		self.assertContains(response, 'aria-label="Business IDs"')
		self.assertContains(response, 'BIZ-1001')
		self.assertContains(response, 'BIZ-1002')
		self.assertContains(response, 'Active')
		self.assertContains(response, 'Inactive')
		self.assertContains(response, 'http://testserver/business/alex-rivera/')
		self.assertContains(response, reverse('edit_business_profile', args=['alex-rivera']))
		self.assertContains(response, reverse('download_profile_card', args=['alex-rivera']))
		self.assertNotContains(response, reverse('download_profile_card', args=['inactive-business']))
		self.assertContains(response, '/media/qr_codes/alex-rivera.png')
		self.assertContains(response, 'Download QR')
		self.assertContains(response, 'alex-rivera-qr.png')
		self.assertNotContains(response, 'PORT-1003')

	def test_dashboard_offers_qr_download_for_non_business_profiles(self):
		profile = self.create_profile(
			profile_type=DigitalProfile.ProfileType.PORTFOLIO_ID,
			slug='portfolio-entry',
			unique_id='PORT-1003',
			display_name='Portfolio Entry',
			qr_code='qr_codes/portfolio-entry.png',
		)
		self.client.force_login(self.staff_user)

		response = self.client.get(reverse('dashboard_home'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			f'href="{profile.qr_code.url}" download="{profile.slug}-qr.png">Download QR</a>',
		)

	def test_dashboard_shows_qr_unavailable_in_both_tables_without_generating_qr(self):
		self.create_profile()
		self.client.force_login(self.staff_user)

		with patch('profiles.models.qrcode.make') as make_qr:
			response = self.client.get(reverse('dashboard_home'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.count(b'QR unavailable'), 2)
		make_qr.assert_not_called()

	def test_staff_can_create_profile_with_selected_color_theme(self):
		self.client.force_login(self.staff_user)

		response = self.client.post(reverse('create_profile'), {
			'client': str(self.client_record.pk),
			'unique_id': 'BIZ-2001',
			'first_name': 'Jordan',
			'last_name': 'Lee',
			'display_name': 'Jordan Lee',
			'color_theme': DigitalProfile.ColorTheme.SUNSET,
		})

		self.assertRedirects(response, reverse('dashboard_home'))
		profile = DigitalProfile.objects.get(display_name='Jordan Lee')
		self.assertEqual(profile.color_theme, DigitalProfile.ColorTheme.SUNSET)
		self.assertEqual(profile.created_by, self.staff_user)

	def test_profile_creation_rejects_unsupported_color_theme(self):
		self.client.force_login(self.staff_user)

		response = self.client.post(reverse('create_profile'), {
			'client': str(self.client_record.pk),
			'unique_id': 'BIZ-2002',
			'first_name': 'Jordan',
			'last_name': 'Lee',
			'display_name': 'Jordan Lee',
			'color_theme': 'NEON',
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(DigitalProfile.objects.count(), 0)
		self.assertIn('color_theme', response.context['form'].errors)

	def test_edit_action_requires_staff_and_saves_profile(self):
		profile = self.create_profile()
		edit_url = reverse('edit_business_profile', args=[profile.slug])

		self.assertEqual(self.client.get(edit_url).status_code, 302)
		self.client.force_login(self.staff_user)
		response = self.client.post(edit_url, {
			'unique_id': 'BIZ-1001',
			'slug': 'alex-rivera',
			'first_name': 'Alex',
			'last_name': 'Rivera',
			'display_name': 'Alex Rivera Updated',
			'title': '',
			'department': '',
			'organization': str(self.organization.pk),
			'phone': '',
			'email': '',
			'website': '',
			'address': '',
			'bio': '',
			'linkedin_url': '',
			'whatsapp_number': '',
			'is_active': 'on',
		})

		self.assertRedirects(response, reverse('dashboard_home'))
		profile.refresh_from_db()
		self.assertEqual(profile.display_name, 'Alex Rivera Updated')
