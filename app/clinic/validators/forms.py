"""Form validators for the clinic app."""
from clinic.config.levels import UserLevel
from clinic.config.messages import (ERROR_DOCTOR_BUSY,
                                    ERROR_DOCTOR_NOT_AVAILABLE,
                                    ERROR_FIRST_NAME_FORMAT,
                                    ERROR_FIRST_NAME_LENGTH,
                                    ERROR_FIRST_NAME_REQUIRED,
                                    ERROR_LAST_NAME_FORMAT,
                                    ERROR_LAST_NAME_LENGTH,
                                    ERROR_LAST_NAME_REQUIRED,
                                    ERROR_SCHEDULE_EXISTS,
                                    ERROR_SPECIALIZATION_FORMAT,
                                    ERROR_START_BEFORE_END,
                                    ERROR_STATUS_SCHEDULED_INVALID,
                                    ERROR_STATUS_VISITED_INVALID,
                                    ERROR_TIME_INCREMENT,
                                    ERROR_USERNAME_UNSAFE,
                                    ERROR_VISIT_OUT_OF_SCHEDULE)
from clinic.config.models import FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH
from clinic.models import Schedule, Visit
from django.core.exceptions import ValidationError
from python_usernames import is_safe_username

TIME_INCREMENT = 15


def validate_time_order(start, end):
    """Validate that the start time is before the end time.

    Args:
        start (datetime.time): The start time.
        end (datetime.time): The end time.

    Raises:
        ValidationError: If the start time is after the end time.
    """
    if start >= end:
        raise ValidationError(ERROR_START_BEFORE_END)


def validate_time_increment(time, increment: int = TIME_INCREMENT):
    """Validate that the time is in increments of the specified value.

    Args:
        time (datetime.time): The time to validate.
        increment (int): The increment value.

    Raises:
        ValidationError: If the time is not in increments of the specified value.
    """
    if time.minute % increment != 0:
        raise ValidationError(ERROR_TIME_INCREMENT)


def validate_doctor_availability(doctor, date, start, end, visit_instance_id, patient):
    """Validate that the doctor is available at the specified time.

    Args:
        doctor (CustomUser): The doctor.
        date (datetime.date): The date of the visit.
        start (datetime.time): The start time of the visit.
        end (datetime.time): The end time of the visit.
        visit_instance_id (str): The ID of the visit instance.
        patient (CustomUser): The patient.
    """
    day_of_week = date.weekday()
    available_schedule = _get_available_schedule(doctor, day_of_week, start, end)

    _check_overlapping_visits(doctor, date, start, end, visit_instance_id, patient)

    _check_schedule_limits(available_schedule, start, end)


def _get_available_schedule(doctor, day_of_week, start, end):
    available_schedule = Schedule.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        start__lte=start,
        end__gte=end,
    )

    if not available_schedule.exists():
        raise ValidationError(ERROR_DOCTOR_NOT_AVAILABLE)

    return available_schedule


def _check_overlapping_visits(doctor, date, start, end, visit_instance_id, patient):
    overlapping_visits = Visit.objects.filter(
        doctor=doctor,
        date=date,
        start__lt=end,
        end__gt=start,
    ).exclude(id=visit_instance_id)

    if overlapping_visits.exists():
        other_patient_visits = overlapping_visits.filter(patient=patient)
        if other_patient_visits.exists():
            busy_time = overlapping_visits.first()
            raise ValidationError(
                ERROR_DOCTOR_BUSY.format(busy_time=busy_time),
            )


def _check_schedule_limits(available_schedule, start, end):
    for schedule in available_schedule:
        if start < schedule.start or end > schedule.end:
            raise ValidationError(ERROR_VISIT_OUT_OF_SCHEDULE)


def validate_schedule(doctor, day_of_week, start, end):
    """Validate that the doctor has a schedule for the specified day of the week.

    Args:
        doctor (CustomUser): The doctor.
        day_of_week (int): The day of the week (0-6, where 0 is Monday).
        start (datetime.time): The start time of the visit.
        end (datetime.time): The end time of the visit.

    Raises:
        ValidationError: If the doctor does not have a schedule for the specified day of the week.
    """
    schedule = Schedule.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        start__lte=start,
        end__gte=end,
    )
    if not schedule.exists():
        raise ValidationError(ERROR_DOCTOR_NOT_AVAILABLE)


def validate_status(status, visit_datetime, current_datetime):
    """Validate the status of the visit based on the visit date and time.

    Args:
        status (str): The status of the visit.
        visit_datetime (datetime.datetime): The date and time of the visit.
        current_datetime (datetime.datetime): The current date and time.

    Raises:
        ValidationError: If the status is invalid based on the visit date and time.
    """
    if visit_datetime > current_datetime and status == 'visited':
        raise ValidationError(ERROR_STATUS_VISITED_INVALID)

    if visit_datetime <= current_datetime and status == 'scheduled':
        raise ValidationError(ERROR_STATUS_SCHEDULED_INVALID)


def validate_schedule_existence(doctor, day_of_week, instance_id):
    """Validate that a schedule does not already exist for the specified doctor and day of the week.

    Args:
        doctor (CustomUser): The doctor.
        day_of_week (int): The day of the week (0-6, where 0 is Monday).
        instance_id (str): The ID of the instance.

    Raises:
        ValidationError: If a schedule already exists for the specified doctor and day of the week.
    """
    if Schedule.objects.filter(doctor=doctor, day_of_week=day_of_week).exclude(id=instance_id).exists():
        raise ValidationError(ERROR_SCHEDULE_EXISTS)


def validate_user_level(request_user, instance, field):
    """Validate the user level field based on the request user and the instance.

    Args:
        request_user (CustomUser): The request user.
        instance (CustomUser): The instance.
        field (ChoiceField): The user level field.

    Returns:
        ChoiceField: The user level field with updated choices.
    """
    if instance and instance.user_level == UserLevel.SUPERUSER.value:
        field.disabled = True

    if request_user:
        if request_user.user_level == UserLevel.SUPERUSER.value:
            field.choices = [
                (UserLevel.ADMIN.value, 'Admin'),
                (UserLevel.DOCTOR.value, 'Doctor'),
                (UserLevel.PATIENT.value, 'Patient'),
            ]
        else:
            field.choices = [
                (UserLevel.DOCTOR.value, 'Doctor'),
                (UserLevel.PATIENT.value, 'Patient'),
            ]
    return field


def validate_is_active(instance, field):
    """Validate the is_active field based on the instance.

    Args:
        instance (CustomUser): The instance.
        field (BooleanField): The is_active field.

    Returns:
        BooleanField: The is_active field.
    """
    if instance.user_level != UserLevel.DOCTOR.value:
        field.disabled = True
    return field


def validate_username(field) -> str:
    """Validate the username field based on the instance.

    Args:
        field (CharField): The username field.

    Returns:
        str: The username.

    Raises:
        ValidationError: If the username is not safe.
    """
    if not is_safe_username(field):
        raise ValidationError(ERROR_USERNAME_UNSAFE)
    return field


def validate_first_name(name: str) -> str:
    """Validate the first name.

    Args:
        name (str): The first name.

    Returns:
        str: The validated first name.

    Raises:
        ValidationError: If the first name is not valid.
    """
    if not name:
        raise ValidationError(ERROR_FIRST_NAME_REQUIRED)
    if not name.isalpha():
        raise ValidationError(ERROR_FIRST_NAME_FORMAT)
    if len(name) > FIRST_NAME_MAX_LENGTH:
        raise ValidationError(ERROR_FIRST_NAME_LENGTH)
    return name


def validate_last_name(name: str) -> str:
    """Validate the last name.

    Args:
        name (str): The last name.

    Returns:
        str: The validated last name.

    Raises:
        ValidationError: If the last name is not valid.
    """
    if not name:
        raise ValidationError(ERROR_LAST_NAME_REQUIRED)
    if not name.isalpha():
        raise ValidationError(ERROR_LAST_NAME_FORMAT)
    if len(name) > LAST_NAME_MAX_LENGTH:
        raise ValidationError(ERROR_LAST_NAME_LENGTH)
    return name


def validate_specialization(specialization: str) -> str:
    """Validate the specialization field.

    Args:
        specialization (str): The specialization.

    Returns:
        str: The specialization.

    Raises:
        ValidationError: If the specialization is not valid.
    """
    if not specialization.isalpha():
        raise ValidationError(ERROR_SPECIALIZATION_FORMAT)
    return specialization
