from datetime import date, datetime, time

from clinic.config.levels import UserLevel
from clinic.models import CustomUser, Schedule, Visit
from clinic.validators.forms import (validate_doctor_availability,
                                     validate_schedule,
                                     validate_schedule_existence,
                                     validate_status, validate_time_increment,
                                     validate_time_order, validate_username)
from django.core.exceptions import ValidationError
from django.test import TestCase


class ValidatorsFormsTest(TestCase):

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
        Schedule.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start=time(9, 0),
            end=time(17, 0)
        )
        Visit.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=datetime.strptime('2024-01-01', "%Y-%m-%d").date(),
            start=time(10, 0),
            end=time(11, 0),
            status='visited'
        )

    def test_validate_time_order_success(self):
        validate_time_order(time(9, 0), time(10, 0))

    def test_validate_time_order_failure(self):
        with self.assertRaises(ValidationError):
            validate_time_order(time(10, 0), time(9, 0))

    def test_validate_time_increment_success(self):
        validate_time_increment(time(9, 0))

    def test_validate_time_increment_failure(self):
        with self.assertRaises(ValidationError):
            validate_time_increment(time(9, 7))

    def test_validate_doctor_availability_success(self):
        validate_doctor_availability(self.doctor, datetime.strptime('2024-01-01', "%Y-%m-%d").date(), time(11, 0), time(12, 0), None, self.patient)

    def test_validate_doctor_availability_failure(self):
        with self.assertRaises(ValidationError):
            validate_doctor_availability(self.doctor, datetime.strptime('2024-01-01', "%Y-%m-%d").date(), time(10, 30), time(11, 30), None, self.patient)

    def test_validate_schedule_success(self):
        validate_schedule(self.doctor, 0, time(10, 0), time(11, 0))

    def test_validate_schedule_failure(self):
        with self.assertRaises(ValidationError):
            validate_schedule(self.doctor, 0, time(18, 0), time(19, 0))

    def test_validate_status_success(self):
        validate_status('visited', datetime.combine(datetime.strptime('2024-01-01', "%Y-%m-%d").date(), time(11, 0)), datetime.now())

    def test_validate_status_failure(self):
        with self.assertRaises(ValidationError):
            validate_status('scheduled', datetime.combine(datetime.strptime('2024-01-01', "%Y-%m-%d").date(), time(11, 0)), datetime.now())

    def test_validate_schedule_existence_success(self):
        validate_schedule_existence(self.doctor, 1, None)

    def test_validate_schedule_existence_failure(self):
        with self.assertRaises(ValidationError):
            validate_schedule_existence(self.doctor, 0, None)

    def test_validate_username_safe(self):
        self.assertEqual(validate_username('safeusername'), 'safeusername')

    def test_validate_username_unsafe(self):
        with self.assertRaises(ValidationError):
            validate_username('admin')

