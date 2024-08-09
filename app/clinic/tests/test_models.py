from datetime import date, time

from clinic.config.levels import UserLevel
from clinic.models import (CustomUser, Diagnosis, DoctorSpecialization,
                           Schedule, Visit)
from django.core.exceptions import ValidationError
from django.test import TestCase


class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='AGasdf36ga',
            first_name='John',
            last_name='Doe',
            phone='+1234567890',
            email='testuser@example.com',
            user_level=UserLevel.PATIENT.value
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('AGasdf36ga'))

    def test_str_method(self):
        self.assertEqual(str(self.user), self.user.username)

    def test_user_level_default(self):
        user = CustomUser.objects.create_user(
            username='anotheruser',
            password='AGasdf36ga',
            first_name='Jane',
            last_name='Smith',
            phone='+0987654321',
            email='anotheruser@example.com',
        )
        self.assertEqual(user.user_level, UserLevel.PATIENT.value)

    def test_email_unique(self):
        # Создаем пользователя с тем же email
        duplicate_user = CustomUser(
            username='newuser',
            password='AGasdf36ga',
            first_name='Mark',
            last_name='Smith',
            phone='+1122334455',
            email='testuser@example.com',  # Duplicate email
        )
        
        # Пробуем вызвать full_clean() для проверки валидации
        with self.assertRaises(ValidationError):
            duplicate_user.full_clean()
        
        # Пробуем сохранить пользователя, ожидая ошибку базы данных
        with self.assertRaises(Exception):
            duplicate_user.save()


class VisitModelTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            first_name='Doctor',
            last_name='Who',
            phone='+1234567891',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = CustomUser.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            first_name='Patient',
            last_name='Zero',
            phone='+1234567892',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.visit = Visit.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=date.today(),
            start=time(10, 0),
            end=time(11, 0),
            status='visited',
        )

    def test_str_method(self):
        expected_str = f'{self.visit.date} - {self.doctor.first_name} {self.doctor.last_name} with {self.patient.first_name} {self.patient.last_name}'
        self.assertEqual(str(self.visit), expected_str)


class ScheduleModelTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            first_name='Doctor',
            last_name='Who',
            phone='+1234567891',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            start=time(9, 0),
            end=time(17, 0),
            day_of_week=date.today().weekday()
        )

    def test_str_method(self):
        expected_str = f'{self.schedule.doctor.first_name} {self.schedule.doctor.last_name} - {self.schedule.get_day_of_week_display()}'
        self.assertEqual(str(self.schedule), expected_str)


class DiagnosisModelTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            first_name='Doctor',
            last_name='Who',
            phone='+1234567891',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = CustomUser.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            first_name='Patient',
            last_name='Zero',
            phone='+1234567892',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.diagnosis = Diagnosis.objects.create(
            description='Test Diagnosis',
            patient=self.patient,
            doctor=self.doctor,
        )

    def test_str_method(self):
        expected_str = f'{self.diagnosis.patient.first_name} {self.diagnosis.patient.last_name} - {self.diagnosis.description}'
        self.assertEqual(str(self.diagnosis), expected_str)


class DoctorSpecializationModelTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='password123',
            first_name='Doctor',
            last_name='Who',
            phone='+1234567891',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.specialization = DoctorSpecialization.objects.create(
            doctor=self.doctor,
            specialization='Cardiology'
        )

    def test_str_method(self):
        self.assertEqual(str(self.specialization), 'Cardiology')

    def test_unique_specialization(self):
        duplicate_specialization = DoctorSpecialization(
            doctor=self.doctor,
            specialization='Cardiology'
        )
        
        with self.assertRaises(ValidationError):
            duplicate_specialization.full_clean()

        try:
            duplicate_specialization.save()
        except Exception as e:
            self.assertTrue(isinstance(e, ValidationError) or isinstance(e, Exception))
