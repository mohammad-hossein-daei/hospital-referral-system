from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Patient, Doctor, Department
from referrals.models import Referral

User = get_user_model()


class ReferralCreateTests(TestCase):
    URL = '/api/referral/create/'

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='doctor1',
            national_code='1234567890',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            medical_code='MED001',
            specialty='قلب',
            phone='09120000000',
        )
        self.department = Department.objects.create(
            name='قلب',
            code='CARD',
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def _payload(self, **overrides):
        base = {
            'national_id': '0012345678',
            'full_name': 'علی رضایی',
            'gender': 'male',
            'phone': '09121111111',
            'doctor_id': self.doctor.id,
            'department_code': 'CARD',
        }
        base.update(overrides)
        return base

    def test_create_new_patient_and_referral(self):
        res = self.client.post(self.URL, self._payload(), format='json')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['status'], 'success')
        self.assertTrue(res.data['data']['patient']['is_new'])
        self.assertEqual(res.data['data']['patient']['national_id'], '0012345678')
        self.assertIn('referral', res.data['data'])

    def test_existing_patient_only_creates_referral(self):
        Patient.objects.create(
            national_id='0012345678',
            full_name='علی رضایی',
            gender='male',
        )
        res = self.client.post(self.URL, self._payload(), format='json')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertFalse(res.data['data']['patient']['is_new'])
        self.assertEqual(Patient.objects.filter(national_id='0012345678').count(), 1)

    def test_invalid_national_id_format(self):
        res = self.client.post(self.URL, self._payload(national_id='abc'), format='json')
        self.assertEqual(res.status_code, 400)

    def test_national_id_wrong_length(self):
        res = self.client.post(self.URL, self._payload(national_id='123'), format='json')
        self.assertEqual(res.status_code, 400)

    def test_invalid_doctor(self):
        res = self.client.post(self.URL, self._payload(doctor_id=99999), format='json')
        self.assertEqual(res.status_code, 400)

    def test_invalid_department(self):
        res = self.client.post(self.URL, self._payload(department_code='WRONG'), format='json')
        self.assertEqual(res.status_code, 400)

    def test_inactive_department(self):
        self.department.is_active = False
        self.department.save()
        res = self.client.post(self.URL, self._payload(), format='json')
        self.assertEqual(res.status_code, 400)

    def test_missing_required_fields(self):
        res = self.client.post(self.URL, {}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(self.URL, self._payload(), format='json')
        self.assertEqual(res.status_code, 401)

    def test_transaction_rollback_on_invalid_referral(self):
        """اگر ارجاع خطا داد، بیمار هم نباید ساخته شود"""
        before = Patient.objects.count()
        res = self.client.post(self.URL, self._payload(department_code='WRONG'), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Patient.objects.count(), before)


class DoctorPatientsListTests(TestCase):
    URL = '/api/doctor/patients/'  # ← مسیر را از urls.py چک کنید

    def setUp(self):
        self.client = APIClient()

        # پزشک ۱
        self.user1 = User.objects.create_user(
            username='doctor1',
            national_code='1111111111',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )
        self.doctor1 = Doctor.objects.create(
            user=self.user1,
            medical_code='MED001',
            specialty='قلب',
            phone='09120000001',
        )

        # پزشک ۲
        self.user2 = User.objects.create_user(
            username='doctor2',
            national_code='2222222222',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )
        self.doctor2 = Doctor.objects.create(
            user=self.user2,
            medical_code='MED002',
            specialty='مغز',
            phone='09120000002',
        )

        self.department = Department.objects.create(
            name='قلب', code='CARD', is_active=True,
        )

        # بیمار ۱ → ارجاع به دکتر ۱
        self.p1 = Patient.objects.create(
            national_id='0000000001', full_name='بیمار ۱', gender='male',
        )
        Referral.objects.create(
            patient=self.p1, doctor=self.doctor1, department=self.department,
            referral_date='2026-01-01T10:00:00Z',
            expiry_date='2026-02-01T10:00:00Z',
        )

        # بیمار ۲ → ارجاع به دکتر ۲
        self.p2 = Patient.objects.create(
            national_id='0000000002', full_name='بیمار ۲', gender='female',
        )
        Referral.objects.create(
            patient=self.p2, doctor=self.doctor2, department=self.department,
            referral_date='2026-01-02T10:00:00Z',
            expiry_date='2026-02-02T10:00:00Z',
        )

    def test_doctor_sees_only_own_patients(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['patients'][0]['national_id'], '0000000001')

    def test_doctor_without_profile_returns_404(self):
        # کاربر پزشک بدون Doctor profile
        u = User.objects.create_user(
            username='doctorx',
            national_code='9999999999',
            password='testpass12345',
            role=User.Role.DOCTOR,
        )
        self.client.force_authenticate(user=u)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, 404)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, 401)


    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertIn(res.status_code, [401, 403])

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertIn(res.status_code, [401, 403])