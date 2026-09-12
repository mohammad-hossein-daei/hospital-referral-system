from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# ═══════════════════════════════════════════════════════════
# TEST: Login / Logout / CurrentUser / CheckAuth
# ═══════════════════════════════════════════════════════════

class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoctor',
            national_code='1234567890',
            password='testpass12345',
            role=User.Role.DOCTOR,
            is_active=True,
        )
        self.url = '/api/login/'

    def test_login_success(self):
        res = self.client.post(self.url, {
            'national_code': '1234567890',
            'password': 'testpass12345',
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['user']['national_code'], '1234567890')
        self.assertEqual(res.data['user']['role'], 'doctor')
        self.assertIn('redirect_url', res.data)
        self.assertIn('dashboard_type', res.data)

    def test_wrong_password(self):
        res = self.client.post(self.url, {
            'national_code': '1234567890',
            'password': 'wrongpass',
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_wrong_national_code(self):
        res = self.client.post(self.url, {
            'national_code': '0000000000',
            'password': 'testpass12345',
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post(self.url, {
            'national_code': '1234567890',
            'password': 'testpass12345',
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_invalid_national_code_format(self):
        res = self.client.post(self.url, {
            'national_code': 'abc',
            'password': 'testpass12345',
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_missing_fields(self):
        res = self.client.post(self.url, {}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_login_admin_role(self):
        admin = User.objects.create_user(
            username='admin1',
            national_code='1111111111',
            password='testpass12345',
            role=User.Role.ADMIN,
        )
        res = self.client.post(self.url, {
            'national_code': '1111111111',
            'password': 'testpass12345',
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['dashboard_type'], 'admin')
        self.assertEqual(res.data['redirect_url'], '/admin/dashboard/')


class LogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoctor',
            national_code='1234567890',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )

    def test_logout_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/logout/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['success'])

    def test_logout_unauthenticated(self):
        res = self.client.post('/api/logout/')
        self.assertEqual(res.status_code, 401)


class CurrentUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoctor',
            national_code='1234567890',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )

    def test_current_user_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/user/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['national_code'], '1234567890')

    def test_current_user_unauthenticated(self):
        res = self.client.get('/api/user/')
        self.assertEqual(res.status_code, 401)


class CheckAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoctor',
            national_code='1234567890',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )

    def test_check_auth_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/check-auth/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['is_authenticated'])
        self.assertEqual(res.data['role'], 'doctor')

    def test_check_auth_unauthenticated(self):
        res = self.client.get('/api/check-auth/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data['is_authenticated'])

    def test_logout_unauthenticated(self):
        res = self.client.post('/api/logout/')
        self.assertIn(res.status_code, [401, 403])

    def test_current_user_unauthenticated(self):
        res = self.client.get('/api/user/')
        self.assertIn(res.status_code, [401, 403])

    def test_check_auth_unauthenticated(self):
        res = self.client.get('/api/check-auth/')
        self.assertEqual(res.status_code, 200)   # ← با AllowAny این درست می‌شود
        self.assertFalse(res.data['is_authenticated'])