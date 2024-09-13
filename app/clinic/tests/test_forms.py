from datetime import date, datetime, time

from clinic.config.levels import UserLevel
from clinic.forms import (CustomUserChangeForm, CustomUserCreationForm,
                          DiagnosisForm, DoctorSearchForm, RegisterUserForm,
                          ScheduleForm, VisitCreationForm, VisitForm)
from clinic.models import CustomUser, Schedule
from django.test import TestCase


class VisitFormTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='ComplexPass123!',
            first_name='Doctor',
            last_name='Who',
            phone='+79409999990',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = CustomUser.objects.create_user(
            username='patient',
            password='ComplexPass123!',
            first_name='Patient',
            last_name='Zero',
            phone='+79409999991',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            start=time(9, 0),
            end=time(17, 0),
            day_of_week=0
        )
        self.valid_data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'date': datetime.strptime('2024-01-01', '%Y-%m-%d').date(),
            'start': time(10, 0),
            'end': time(11, 0),
            'status': 'visited',
            'description': 'Regular check-up',
        }

    def test_valid_form(self):
        form = VisitForm(data=self.valid_data)
        if not form.is_valid():
            print(form.errors)
            print(self.valid_data, form.cleaned_data)
        self.assertTrue(form.is_valid())

    def test_invalid_time_order(self):
        invalid_data = self.valid_data.copy()
        invalid_data['start'] = time(11, 0)
        invalid_data['end'] = time(10, 0)
        form = VisitForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_clean_method(self):
        form = VisitForm(data=self.valid_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())


class ScheduleFormTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='Gasfa3gasf!',
            first_name='Doctor',
            last_name='Who',
            phone='+79409999992',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.valid_data = {
            'doctor': self.doctor.id,
            'start': time(9, 0),
            'end': time(17, 0),
            'day_of_week': 1,
        }

    def test_valid_form(self):
        form = ScheduleForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_time_order(self):
        invalid_data = self.valid_data.copy()
        invalid_data['start'] = time(11, 0)
        invalid_data['end'] = time(10, 0)
        form = VisitForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class DiagnosisFormTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='Gasfa3gasf!',
            first_name='Doctor',
            last_name='Who',
            phone='+79409999993',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = CustomUser.objects.create_user(
            username='patient',
            password='Gasfa3gasf!',
            first_name='Patient',
            last_name='Zero',
            phone='+79409999994',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.valid_data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'description': 'Valid Diagnosis Description',
        }

    def test_valid_form(self):
        form = DiagnosisForm(data=self.valid_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_short_description(self):
        invalid_data = self.valid_data.copy()
        invalid_data['description'] = 'Short'
        form = DiagnosisForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)


class CustomUserCreationFormTest(TestCase):

    def test_valid_form(self):
        valid_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'phone': '+79409999995',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf!',
            'user_level': UserLevel.PATIENT.value,
        }
        form = CustomUserCreationForm(data=valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_doctor_creation(self):
        valid_data = {
            'username': 'doctoruser',
            'first_name': 'Doctor',
            'last_name': 'User',
            'email': 'doctoruser@example.com',
            'phone': '+79409999999',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf!',
            'user_level': UserLevel.DOCTOR.value,
        }
        form = CustomUserCreationForm(data=valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'doctoruser')
        self.assertFalse(user.is_active)

    def test_admin_creation(self):
        valid_data = {
            'username': 'adminuser',
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'adminuser@example.com',
            'phone': '+79409999999',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf!',
            'user_level': UserLevel.ADMIN.value,
        }
        form = CustomUserCreationForm(data=valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_password_mismatch(self):
        invalid_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser2@example.com',
            'phone': '+79409999916',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf6',
        }
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class CustomUserChangeFormTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='changetestuser',
            password='ComplexPass123!',
            first_name='Change',
            last_name='User',
            phone='+79409999900',
            email='changetestuser@example.com',
            user_level=UserLevel.PATIENT.value
        )

    def test_save_changes(self):
        form = CustomUserChangeForm(data={
            'username': 'changeduser',
            'first_name': 'Changed',
            'last_name': 'User',
            'email': 'changeduser@example.com',
            'phone': '+79409999901',
            'user_level': UserLevel.PATIENT.value
        }, instance=self.user)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'changeduser')
        self.assertEqual(user.first_name, 'Changed')

    def test_save_admin(self):
        self.user.user_level = UserLevel.ADMIN.value
        self.user.save()
        form = CustomUserChangeForm(data={
            'username': 'changedadmin',
            'first_name': 'Changed',
            'last_name': 'Admin',
            'email': 'changedadmin@example.com',
            'phone': '+79409999902',
            'user_level': UserLevel.ADMIN.value
        }, instance=self.user)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class RegisterUserFormTest(TestCase):

    def test_valid_form(self):
        valid_data = {
            'username': 'registeruser',
            'first_name': 'Register',
            'last_name': 'User',
            'email': 'registeruser@example.com',
            'phone': '+79409999997',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf!',
        }
        form = RegisterUserForm(data=valid_data)
        self.assertTrue(form.is_valid())

    def test_clean_method(self):
        invalid_data = {
            'username': 'registeruser',
            'first_name': 'Register',
            'last_name': '',
            'email': 'invalid-email',
            'phone': '1234567890',
            'password1': 'Gasfa3gasf!',
            'password2': 'Gasfa3gasf!',
        }
        form = RegisterUserForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('phone', form.errors)


class VisitCreationFormTest(TestCase):

    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            username='doctor',
            password='ComplexPass123!',
            first_name='Doctor',
            last_name='Who',
            phone='+79409999990',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = CustomUser.objects.create_user(
            username='patient',
            password='ComplexPass123!',
            first_name='Patient',
            last_name='Zero',
            phone='+79409999991',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            start=time(9, 0),
            end=time(17, 0),
            day_of_week=0
        )
        self.valid_data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'date': datetime.strptime('2024-01-01', '%Y-%m-%d').date(),
            'start': time(10, 0),
            'end': time(11, 0),
            'status': 'visited',
            'description': 'Regular check-up',
        }

    def test_valid_form(self):
        form = VisitForm(data=self.valid_data)
        if not form.is_valid():
            print(form.errors)
            print(self.valid_data, form.cleaned_data)
        self.assertTrue(form.is_valid())

    def test_invalid_time_order(self):
        invalid_data = self.valid_data.copy()
        invalid_data['start'] = time(11, 0)
        invalid_data['end'] = time(10, 0)
        form = VisitForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_clean_method(self):
        form = VisitForm(data=self.valid_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())


class DoctorSearchFormTest(TestCase):

    def test_no_search_parameters(self):
        form = DoctorSearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_valid_search_parameters(self):
        valid_data = {
            'first_name': 'Doctor',
        }
        form = DoctorSearchForm(data=valid_data)
        self.assertTrue(form.is_valid())
