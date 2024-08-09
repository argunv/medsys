from clinic.config.levels import UserLevel
from clinic.config.tests import (ADMIN_PHONE, DAY_OF_WEEK_ONE,  # noqa: WPS235
                                 DAY_OF_WEEK_TWO, DOCTOR_EMAIL,
                                 DOCTOR_USERNAME, HOME_URL, OVERLAP_END_TIME,
                                 OVERLAP_START_TIME, PASSWORD,
                                 PATIENT_USERNAME, PHONE_THREE,
                                 SUPERUSER_EMAIL, SUPERUSER_PHONE,
                                 SUPERUSER_USERNAME, WORK_END_TIME,
                                 WORK_START_TIME)
from clinic.models import Diagnosis, DoctorSpecialization, Schedule, Visit
from clinic.serializers import (CustomUserSerializer, DiagnosisSerializer,
                                DoctorSpecializationSerializer,
                                ScheduleSerializer, VisitSerializer)
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class CustomUserSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser1@example.com',
            user_level=UserLevel.PATIENT.value,
            phone='+10000000001'
        )
        self.serializer = CustomUserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'user_level']))

    def test_username_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['username'], self.user.username)


class VisitSerializerTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='password123',
            email='doctor1@example.com',
            user_level=UserLevel.DOCTOR.value,
            phone='+10000000002'
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='password123',
            email='patient1@example.com',
            user_level=UserLevel.PATIENT.value,
            phone='+10000000003'
        )
        self.visit = Visit.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date='2024-01-01',
            start='09:00',
            end='10:00',
            status='Active',
            description='Initial consultation'
        )
        self.serializer = VisitSerializer(instance=self.visit)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'doctor', 'patient', 'date', 'start', 'end', 'status', 'description']))

    def test_doctor_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['doctor'], self.doctor.username)


class ScheduleSerializerTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='password123',
            email='doctor2@example.com',
            user_level=UserLevel.DOCTOR.value,
            phone='+10000000004'
        )
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            day_of_week=1,
            start='09:00',
            end='17:00'
        )
        self.serializer = ScheduleSerializer(instance=self.schedule)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'doctor', 'day_of_week', 'start', 'end']))

    def test_doctor_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['doctor'], self.doctor.username)


class DiagnosisSerializerTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='password123',
            email='doctor3@example.com',
            user_level=UserLevel.DOCTOR.value,
            phone='+10000000005'
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='password123',
            email='patient2@example.com',
            user_level=UserLevel.PATIENT.value,
            phone='+10000000006'
        )
        self.diagnosis = Diagnosis.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            description='Test diagnosis'
        )
        self.serializer = DiagnosisSerializer(instance=self.diagnosis)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'doctor', 'patient', 'description', 'is_active', 'created_at']))

    def test_description_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['description'], self.diagnosis.description)


class DoctorSpecializationSerializerTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='password123',
            email='doctor4@example.com',
            user_level=UserLevel.DOCTOR.value,
            phone='+10000000007'
        )
        self.specialization = DoctorSpecialization.objects.create(
            doctor=self.doctor,
            specialization='Cardiology'
        )
        self.serializer = DoctorSpecializationSerializer(instance=self.specialization)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['doctor', 'specialization']))

    def test_specialization_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['specialization'], self.specialization.specialization)


class VisitViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_user(
            username='superuser',
            password='password123',
            email='superuser2@example.com',
            user_level=UserLevel.SUPERUSER.value,
            phone='+10000000010'
        )
        self.doctor = User.objects.create_user(
            username='doctor',
            password='password123',
            email='doctor5@example.com',
            user_level=UserLevel.DOCTOR.value,
            phone='+10000000011'
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='password123',
            email='patient3@example.com',
            user_level=UserLevel.PATIENT.value,
            phone='+10000000012'
        )
        self.visit = Visit.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date='2024-01-01',
            start='09:00',
            end='10:00',
            status='visited',
            description='Initial consultation'
        )
        self.client.login(username='superuser', password='password123')

    def test_visit_create(self):
        data = {
            'doctor': self.doctor.username,
            'patient': self.patient.username,
            'date': '2024-01-02',
            'start': '11:00',
            'end': '12:00',
            'status': 'scheduled',
            'description': 'Follow-up consultation'
        }
        response = self.client.post(reverse('visit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Visit.objects.count(), 2)

    def test_visit_update(self):
        data = {
            'doctor': self.doctor.username,
            'patient': self.patient.username,
            'date': '2024-01-03',
            'start': '11:00',
            'end': '12:00',
            'status': 'scheduled',
            'description': 'Updated consultation'
        }
        response = self.client.put(reverse('visit-detail', kwargs={'pk': self.visit.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.visit.refresh_from_db()
        self.assertEqual(str(self.visit.date), '2024-01-03')


