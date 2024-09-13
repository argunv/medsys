from datetime import date, time

from clinic.config.levels import UserLevel
from clinic.config.models import VisitStatus
from clinic.models import Diagnosis, DoctorSpecialization, Schedule, Visit
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

class MainPageViewTest(TestCase):

    def test_main_page_view(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')


class RegisterViewTest(TestCase):

    def test_register_view_get_anonymous(self):
        response = self.client.get(reverse('register', kwargs={'role': 'patient'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/patient/index.html')

    def test_register_view_get_authenticated(self):
        user = User.objects.create_user(
            username='testpatient1',
            password='AGasdf36ga',
            phone='+79409990604',
            email='testpatient1@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.client.login(username='testpatient1', password='AGasdf36ga')
        response = self.client.get(reverse('profile', kwargs={'username': 'testpatient1'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/patient_profile.html')

    def test_register_view_post(self):
        response = self.client.post(reverse('register', kwargs={'role': 'patient'}), {
            'username': 'newpatient',
            'password1': 'AGasdf36ga',
            'password2': 'AGasdf36ga',
            'phone': '+79409990993',
            'email': 'newpatient@example.com',
            'first_name': 'New',
            'last_name': 'Patient'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newpatient').exists())


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='AGasdf36ga',
            email='testuser@example.com'
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/index.html')

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'AGasdf36ga'})
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'testuser'}))


class LogoutViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='AGasdf36ga',
            email='testuser@example.com'
        )
        self.client.login(username='testuser', password='AGasdf36ga')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class ProfileViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+79409990201',
            email='doctor@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            phone='+1234567891',
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_profile_view_get_own_profile(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'doctor'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/doctor_profile.html')

    def test_profile_view_get_other_profile(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'patient'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/patient_profile_for_doctor.html')

    def test_profile_view_post_patient(self):
        self.client.logout()
        self.client.login(username='patient', password='AGasdf36ga')
        response = self.client.post(reverse('profile', kwargs={'username': 'doctor'}), {
            'date': date.today(),
            'start': time(10, 0).strftime('%H:%M'),
            'end': time(11, 0).strftime('%H:%M'),
            'status': VisitStatus.SCHEDULED.value
        })
        self.assertEqual(response.status_code, 200)


class UpdateScheduleViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+1234567894',
            first_name='Doctor',
            last_name='Who',
            email='doctor_example_af@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            start=time(9, 0),
            end=time(17, 0),
            day_of_week=date.today().weekday()
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_update_schedule_view(self):
        response = self.client.post(reverse('update_schedule', kwargs={'pk': self.schedule.pk}), {
            'day_of_week': date.today().weekday(),
            'start': time(10, 0).strftime('%H:%M'),
            'end': time(16, 0).strftime('%H:%M'),
            'status': VisitStatus.SCHEDULED.value
        })
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'doctor'}))
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.start, time(10, 0))
        self.assertEqual(self.schedule.end, time(16, 0))


class VisitUpdateTest(TestCase):

    def setUp(self):
        self.patient = User.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            phone='+1234567893',
            first_name='Patient',
            last_name='Zero',
            email='patient_example_af@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+1234567894',
            first_name='Doctor',
            last_name='Who',
            email='doctor_example_af@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.visit = Visit.objects.create(
            doctor=self.doctor, patient=self.patient, status=VisitStatus.ACTIVE, date=date.today(), start=time(9, 0), end=time(10, 0)
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_visit_update_get_form_kwargs(self):
        response = self.client.get(reverse('visit_update', kwargs={'pk': self.visit.pk}))  # Исправлено на 'pk'
        form = response.context['form']
        self.assertEqual(form.doctor, self.doctor)
        self.assertEqual(form.patient, self.patient)


class AddDiagnosisViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+794099990100',
            first_name='Doctor',
            last_name='Zero',
            email='doctor_diagnosis@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            phone='+794099990101',
            first_name='Patient',
            last_name='Zero',
            email='patient_diagnosis@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.visit = Visit.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=date.today(),
            start=time(10, 0),
            end=time(11, 0),
            status=VisitStatus.VISITED
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_add_diagnosis_view_get(self):
        response = self.client.get(reverse('add_diagnosis', kwargs={'patient_id': self.patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diagnosis/diagnosis_form.html')

    def test_form_valid(self):
        response = self.client.post(reverse('add_diagnosis', kwargs={'patient_id': self.patient.id}), {
            'description': 'Test diagnosis'
        })

        self.assertRedirects(response, reverse('profile', kwargs={'username': 'doctor'}))
        self.assertTrue(Diagnosis.objects.filter(patient=self.patient, doctor=self.doctor).exists())



class ChangeDiagnosisStatusViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            first_name='Doctor',
            last_name='Zero',
            phone='+79409991000',
            email='doctor_diagnosis@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='AGasdf36ga',
            first_name='Patient',
            last_name='Zero',
            phone='+79409991001',
            email='patient_diagnosis@example.com',
            user_level=UserLevel.PATIENT.value
        )
        self.diagnosis = Diagnosis.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            description='Test Diagnosis'
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_update_diagnosis(self):
        response = self.client.post(reverse('update_diagnosis', kwargs={'pk': self.diagnosis.pk}), {
            'is_active': False
        })
        
        # Добавляем логирование для проверки ошибок формы
        if response.status_code == 200:
            print("Form errors: ", response.context['form'].errors)

        self.assertRedirects(response, reverse('profile', kwargs={'username': 'doctor'}))
        self.diagnosis.refresh_from_db()
        self.assertFalse(self.diagnosis.is_active)


class DoctorSearchViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+79409991002',
            email='doctor_search@example.com',
            first_name='Doctor',
            last_name='Who',
            user_level=UserLevel.DOCTOR.value
        )
        self.specialization = DoctorSpecialization.objects.create(
            doctor=self.doctor,
            specialization='Cardiology'
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_doctor_search_view_get(self):
        response = self.client.get(reverse('search_doctors'), {'first_name': 'Doc'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_doctors.html')
        self.assertContains(response, 'Cardiology')


class DoctorSpecializationUpdateViewTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor',
            password='AGasdf36ga',
            phone='+79409991003',
            first_name='Doctor',
            last_name='Who',
            email='doctor_specialization@example.com',
            user_level=UserLevel.DOCTOR.value
        )
        self.specialization = DoctorSpecialization.objects.create(
            doctor=self.doctor,
            specialization='Cardiology'
        )
        self.client.login(username='doctor', password='AGasdf36ga')

    def test_specialization_update_view_get(self):
        response = self.client.get(reverse('specialization_update', kwargs={'pk': self.specialization.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/doctor_specialization_update.html')

    def test_specialization_update_view_post(self):
        data = {'specialization': 'Neurology'}
        response = self.client.post(reverse('specialization_update', kwargs={'pk': self.specialization.pk}), data)
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'doctor'}))
        self.specialization.refresh_from_db()
        self.assertEqual(self.specialization.specialization, 'Neurology')
