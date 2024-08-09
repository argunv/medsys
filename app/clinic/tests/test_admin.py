"""Test cases for admin classes."""

from clinic.admin import (CustomUserAdmin, DiagnosisAdmin,
                          DoctorSpecializationAdmin, ScheduleAdmin, VisitAdmin)
from clinic.config.levels import UserLevel
from clinic.config.tests import (ADMIN_PHONE, DAY_OF_WEEK_ONE,  # noqa: WPS235
                                 DAY_OF_WEEK_TWO, DOCTOR_EMAIL,
                                 DOCTOR_USERNAME, HOME_URL, OVERLAP_END_TIME,
                                 OVERLAP_START_TIME, PASSWORD,
                                 PATIENT_USERNAME, PHONE_THREE,
                                 SUPERUSER_EMAIL, SUPERUSER_PHONE,
                                 SUPERUSER_USERNAME, WORK_END_TIME,
                                 WORK_START_TIME)
from clinic.models import (CustomUser, Diagnosis, DoctorSpecialization,
                           Schedule, Visit)
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

User = get_user_model()


class CustomUserAdminTest(TestCase):
    """Test cases for the CustomUserAdmin class."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data for the CustomUserAdmin class."""
        cls.factory = RequestFactory()
        cls.superuser = User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            password=PASSWORD,
            email=SUPERUSER_EMAIL,
            phone=SUPERUSER_PHONE,
        )
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            password=PASSWORD,
            email='adminuser@example.com',
            user_level=UserLevel.ADMIN.value,
            is_staff=True,
            phone=ADMIN_PHONE,
        )

    def setUp(self):
        """Set up the test for the CustomUserAdminTest class."""
        self.client.login(username=SUPERUSER_USERNAME, password=PASSWORD)

    def test_get_readonly_fields(self):
        """Test the get_readonly_fields method."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = CustomUserAdmin(CustomUser, admin.site)
        readonly_fields = model_admin.get_readonly_fields(request)
        self.assertIn('last_login', readonly_fields)
        self.assertIn('date_joined', readonly_fields)

    def test_has_delete_permission(self):
        """Test the has_delete_permission method."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = CustomUserAdmin(CustomUser, admin.site)
        user = CustomUser(
            username='testuser',
            user_level=UserLevel.ADMIN.value,
            phone=PHONE_THREE)
        has_permission = model_admin.has_delete_permission(request, user_obj=user)
        self.assertTrue(has_permission)

    def test_get_queryset(self):
        """Test the get_queryset method."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = CustomUserAdmin(CustomUser, admin.site)
        queryset = model_admin.get_queryset(request)
        self.assertIn(self.admin_user, queryset)

    def test_get_form(self):
        """Test the get_form method for the CustomUserAdminTest class."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = CustomUserAdmin(CustomUser, admin.site)
        form = model_admin.get_form(request)
        self.assertIn('user_level', form.base_fields)
        self.assertIn('phone', form.base_fields)

    def test_save_model(self):
        """Test the save_model method."""
        request = self.factory.post(HOME_URL)
        request.user = self.superuser

        model_admin = CustomUserAdmin(CustomUser, admin.site)
        user = CustomUser(username=DOCTOR_USERNAME,
                          user_level=UserLevel.DOCTOR.value,
                          phone=PHONE_THREE)
        model_admin.save_model(request, user, form=None, change=False)

        self.assertTrue(user.is_active)


class VisitAdminTest(TestCase):
    """Test cases for the VisitAdmin class."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data for the VisitAdmin class."""
        cls.factory = RequestFactory()
        cls.superuser = User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            password=PASSWORD,
            email=SUPERUSER_EMAIL,
            phone=SUPERUSER_PHONE,
        )
        cls.doctor = User.objects.create_user(
            username=DOCTOR_USERNAME,
            password=PASSWORD,
            email=DOCTOR_EMAIL,
            user_level=UserLevel.DOCTOR.value,
            phone=ADMIN_PHONE,
        )
        cls.patient = User.objects.create_user(
            username=PATIENT_USERNAME,
            password=PASSWORD,
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value,
            phone=PHONE_THREE,
        )

    def setUp(self):
        """Set up the test for the VisitAdminTest class."""
        self.client.login(username=SUPERUSER_USERNAME, password=PASSWORD)

    def test_get_form(self):
        """Test the get_form method for the VisitAdminTest class."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = VisitAdmin(Visit, admin.site)
        form = model_admin.get_form(request)

        self.assertIn(DOCTOR_USERNAME, form.base_fields)
        self.assertIn(PATIENT_USERNAME, form.base_fields)
        self.assertEqual(form.base_fields[DOCTOR_USERNAME].queryset.count(), 1)
        self.assertEqual(form.base_fields[PATIENT_USERNAME].queryset.count(), 1)


class ScheduleAdminTest(TestCase):
    """Test cases for the ScheduleAdmin class."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data for the ScheduleAdmin class."""
        cls.factory = RequestFactory()
        cls.superuser = User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            password=PASSWORD,
            email=SUPERUSER_EMAIL,
            phone=SUPERUSER_PHONE,
        )
        cls.doctor = User.objects.create_user(
            username=DOCTOR_USERNAME,
            password=PASSWORD,
            email=DOCTOR_EMAIL,
            user_level=UserLevel.DOCTOR.value,
            phone=ADMIN_PHONE,
        )

    def setUp(self):
        """Set up the test for the ScheduleAdminTest class."""
        self.client.login(username=SUPERUSER_USERNAME, password=PASSWORD)

    def test_is_schedule_overlapping(self):
        """Test the _is_schedule_overlapping method."""
        Schedule.objects.create(
            doctor=self.doctor,
            start=WORK_START_TIME,
            end=WORK_END_TIME,
            day_of_week=DAY_OF_WEEK_ONE,
        )

        overlapping_schedule = Schedule(
            doctor=self.doctor,
            start=OVERLAP_START_TIME,
            end=OVERLAP_END_TIME,
            day_of_week=DAY_OF_WEEK_ONE,
        )

        model_admin = ScheduleAdmin(Schedule, admin.site)
        is_overlapping = model_admin._is_schedule_overlapping(overlapping_schedule)  # noqa: WPS437
        self.assertTrue(is_overlapping)

    def test_get_form(self):
        """Test the get_form method for the ScheduleAdminTest class."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = ScheduleAdmin(Schedule, admin.site)
        form = model_admin.get_form(request)

        self.assertIn(DOCTOR_USERNAME, form.base_fields)
        self.assertEqual(form.base_fields[DOCTOR_USERNAME].queryset.count(), 1)

    def test_save_model(self):
        """Test the save_model method."""
        request = self.factory.post(HOME_URL)
        request.user = self.superuser

        model_admin = ScheduleAdmin(Schedule, admin.site)
        schedule = Schedule(doctor=self.doctor,
                            start=WORK_START_TIME,
                            end=WORK_END_TIME,
                            day_of_week=DAY_OF_WEEK_TWO)
        model_admin.save_model(request, schedule, form=None, change=False)

        self.assertTrue(schedule.pk is not None)


class DiagnosisAdminTest(TestCase):
    """Test cases for the DiagnosisAdmin class."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data for the DiagnosisAdmin class."""
        cls.factory = RequestFactory()
        cls.superuser = User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            password=PASSWORD,
            email=SUPERUSER_EMAIL,
            phone=SUPERUSER_PHONE,
        )
        cls.doctor = User.objects.create_user(
            username=DOCTOR_USERNAME,
            password=PASSWORD,
            email=DOCTOR_EMAIL,
            user_level=UserLevel.DOCTOR.value,
            is_active=True,
            phone=ADMIN_PHONE,
        )
        cls.patient = User.objects.create_user(
            username=PATIENT_USERNAME,
            password=PASSWORD,
            email='patient@example.com',
            user_level=UserLevel.PATIENT.value,
            phone=PHONE_THREE,
        )

    def setUp(self):
        """Set up the test for the DiagnosisAdminTest class."""
        self.client.login(username=SUPERUSER_USERNAME, password=PASSWORD)

    def test_get_form(self):
        """Test the get_form method for the DiagnosisAdminTest class."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = DiagnosisAdmin(Diagnosis, admin.site)
        form = model_admin.get_form(request)

        self.assertIn(DOCTOR_USERNAME, form.base_fields)
        self.assertIn(PATIENT_USERNAME, form.base_fields)
        self.assertEqual(form.base_fields[DOCTOR_USERNAME].queryset.count(), 1)
        self.assertEqual(form.base_fields[PATIENT_USERNAME].queryset.count(), 1)


class DoctorSpecializationAdminTest(TestCase):
    """Test cases for the DoctorSpecializationAdmin class."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data for the DoctorSpecializationAdmin class."""
        cls.factory = RequestFactory()
        cls.superuser = User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            password=PASSWORD,
            email=SUPERUSER_EMAIL,
            phone=SUPERUSER_PHONE,
        )
        cls.doctor = User.objects.create_user(
            username=DOCTOR_USERNAME,
            password=PASSWORD,
            email=DOCTOR_EMAIL,
            user_level=UserLevel.DOCTOR.value,
            is_active=True,
            phone=ADMIN_PHONE,
        )

    def setUp(self):
        """Set up the test for the DoctorSpecializationAdminTest class."""
        self.client.login(username=SUPERUSER_USERNAME, password=PASSWORD)

    def test_get_form(self):
        """Test the get_form method for the DoctorSpecializationAdminTest class."""
        request = self.factory.get(HOME_URL)
        request.user = self.superuser

        model_admin = DoctorSpecializationAdmin(DoctorSpecialization, admin.site)
        form = model_admin.get_form(request)

        self.assertIn(DOCTOR_USERNAME, form.base_fields)
        self.assertEqual(form.base_fields[DOCTOR_USERNAME].queryset.count(), 1)
