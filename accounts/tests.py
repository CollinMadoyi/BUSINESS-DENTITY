from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminBrandingTests(TestCase):
    def setUp(self):
        staff_user = get_user_model().objects.create_superuser(
            username='admin-branding',
            email='admin-branding@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)

    def test_admin_homepage_uses_django_default_branding(self):
        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')
        self.assertNotContains(response, 'linear-gradient(110deg, #12304a, #1e5372)')

    def test_admin_model_pages_are_registered_and_render(self):
        model_pages = (
            'admin:accounts_customuser_changelist',
            'admin:organizations_organization_changelist',
            'admin:profiles_client_changelist',
            'admin:profiles_digitalprofile_changelist',
            'admin:students_studentrecord_changelist',
            'admin:companies_companyprofile_changelist',
            'admin:companies_companymember_changelist',
            'admin:portfolio_portfolioprofile_changelist',
            'admin:portfolio_portfolioproject_changelist',
            'admin:contacts_contactrecord_changelist',
            'admin:qrcode_manager_qrcoderecord_changelist',
        )
        for page_name in model_pages:
            with self.subTest(page_name=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
