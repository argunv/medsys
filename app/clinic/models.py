"""Models for the clinic application."""

import uuid

from django.contrib.auth.models import (AbstractUser, BaseUserManager, Group,
                                        Permission)
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from .config.levels import UserLevel, UserLimitChoices
from .config.models import (DAY_OF_WEEK_CHOICES, FIRST_NAME_MAX_LENGTH,
                            LAST_NAME_MAX_LENGTH, SPECIALTY_MAX_LENGTH,
                            STATUS_CHOICES, STATUS_MAX_LENGTH)
from .validators.models import (validate_first_name, validate_last_name,
                                validate_specialty)


class UUIDMixin(models.Model):
    """Mixin to add UUID as the primary key."""

    id: models.UUIDField = models.UUIDField(primary_key=True,
                                            default=uuid.uuid4,
                                            editable=False)

    class Meta:
        """Meta class for the UUIDMixin."""

        abstract = True


class CustomUserManager(BaseUserManager):
    """User manager for creating regular users and superusers."""

    def create_user(self, username: str, password: str = None, **extra_fields) -> 'CustomUser':
        """
        Create a regular user.

        Parameters:
            username (str): Username
            password (str): User password
            extra_fields: Additional fields

        Returns:
            CustomUser: Created user
        """
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str = None, **extra_fields) -> 'CustomUser':
        """
        Create a superuser.

        Parameters:
            username (str): Username
            password (str): User password
            extra_fields: Additional fields

        Returns:
            CustomUser: Created superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_level', 3)

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser, UUIDMixin):
    """User model with additional fields and roles."""

    first_name: models.CharField = models.CharField('first name',
                                                    max_length=FIRST_NAME_MAX_LENGTH,
                                                    blank=False,
                                                    validators=[validate_first_name])
    last_name: models.CharField = models.CharField('last name',
                                                   max_length=LAST_NAME_MAX_LENGTH,
                                                   blank=False,
                                                   validators=[validate_last_name])
    phone: PhoneNumberField = PhoneNumberField(null=False, blank=False, unique=True)
    email: models.EmailField = models.EmailField(null=False, blank=False, unique=True)
    user_level: models.SmallIntegerField = models.SmallIntegerField(
        choices=UserLevel.choices,
        default=UserLevel.PATIENT.value)

    objects: CustomUserManager = CustomUserManager()  # noqa: WPS110

    groups: models.ManyToManyField = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'
        ),
        verbose_name='groups',
    )
    user_permissions: models.ManyToManyField = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self) -> str:
        """Return the string representation of the user.

        Returns:
            str: The string representation of the user.
        """
        return self.username

    class Meta:
        """Meta class for the CustomUser."""

        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Visit(UUIDMixin):
    """Model for a doctor's visit."""

    doctor: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_visits',
        limit_choices_to=UserLimitChoices.DOCTOR)
    patient: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient_visits',
        limit_choices_to=UserLimitChoices.PATIENT)
    date: models.DateField = models.DateField()
    start: models.TimeField = models.TimeField()
    end: models.TimeField = models.TimeField()
    status: models.CharField = models.CharField(max_length=STATUS_MAX_LENGTH,
                                                choices=STATUS_CHOICES,
                                                default=STATUS_CHOICES[0][0])
    description: models.TextField = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        """Return the string representation of the visit.

        Returns:
            str: The string representation of the visit.
        """
        date: str = self.date
        doctor_name: str = f'{self.doctor.first_name} {self.doctor.last_name}'
        patient_name: str = f'{self.patient.first_name} {self.patient.last_name}'

        return f'{date} - {doctor_name} with {patient_name}'

    class Meta:
        """Meta class for the Visit."""

        permissions: list[tuple[str, str]] = [
            ('can_view_visit', 'Can view visit'),
            ('can_edit_visit', 'Can edit visit'),
        ]
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'


class Schedule(UUIDMixin):
    """Model for a doctor's schedule."""

    doctor: models.ForeignKey = models.ForeignKey(CustomUser,
                                                  on_delete=models.CASCADE,
                                                  related_name='doctor_schedule',
                                                  limit_choices_to=UserLimitChoices.DOCTOR)
    start: models.TimeField = models.TimeField(blank=False, null=False)
    end: models.TimeField = models.TimeField(blank=False, null=False)
    day_of_week: models.SmallIntegerField = models.SmallIntegerField(choices=DAY_OF_WEEK_CHOICES)

    def get_day_of_week_display(self) -> str:
        """Return the display name of the day of the week.

        Returns:
            str: The display name of the day of the week.
        """
        return dict(DAY_OF_WEEK_CHOICES)[self.day_of_week]

    def __str__(self) -> str:
        """Return the string representation of the schedule.

        Returns:
            str: The string representation of the schedule.
        """
        return f'{self.doctor.first_name} {self.doctor.last_name} - {self.get_day_of_week_display()}'

    class Meta:
        """Meta class for the Schedule."""

        permissions: list[tuple[str, str]] = [
            ('can_view_schedule', 'Can view schedule'),
            ('can_edit_schedule', 'Can edit schedule'),
        ]
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'


class Diagnosis(UUIDMixin):
    """Model for a patient's diagnosis."""

    description: models.TextField = models.TextField(blank=True, null=True)
    patient: models.ForeignKey = models.ForeignKey(CustomUser,
                                                   on_delete=models.CASCADE,
                                                   related_name='patient_diagnoses',
                                                   limit_choices_to=UserLimitChoices.PATIENT)
    doctor: models.ForeignKey = models.ForeignKey(CustomUser,
                                                  on_delete=models.CASCADE,
                                                  related_name='doctor_diagnoses',
                                                  limit_choices_to=UserLimitChoices.DOCTOR)
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the string representation of the diagnosis.

        Returns:
            str: The string representation of the diagnosis.
        """
        return f'{self.patient.first_name} {self.patient.last_name} - {self.description}'

    class Meta:
        """Meta class for the Diagnosis."""

        permissions: list[tuple[str, str]] = [
            ('can_view_diagnosis', 'Can view diagnosis'),
            ('can_edit_diagnosis', 'Can edit diagnosis'),
        ]
        verbose_name = 'Diagnosis'
        verbose_name_plural = 'Diagnoses'


class DoctorSpecialization(models.Model):
    """Model for a doctor's specialization."""

    doctor: models.OneToOneField = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_specializations',
        limit_choices_to=UserLimitChoices.DOCTOR,
        primary_key=True,
    )
    specialization: models.CharField = models.CharField(
        max_length=SPECIALTY_MAX_LENGTH,
        blank=False,
        null=False,
        validators=[validate_specialty],
    )

    def __str__(self) -> str:
        """Return the string representation of the specialization.

        Returns:
            str: The string representation of the specialization.
        """
        return self.specialization

    class Meta:
        """Meta class for the DoctorSpecialization."""

        verbose_name = 'Doctor Specialization'
        verbose_name_plural = 'Doctor Specializations'
        unique_together = ('doctor', 'specialization')
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'specialization'],
                                    name='unique_doctor_specialization'),
        ]
