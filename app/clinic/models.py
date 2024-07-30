"""Модели для приложения клиники."""

import uuid

from django.contrib.auth.models import (AbstractUser,
                                        BaseUserManager,
                                        Group,
                                        Permission)
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    """Миксин для добавления UUID в качестве первичного ключа."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей для создания обычных пользователей и суперпользователей."""

    def create_user(self, username, password=None, **extra_fields):
        """
        Создание обычного пользователя.

        Parameters:
            username (str): Имя пользователя
            password: Пароль пользователя
            **extra_fields: Дополнительные поля

        Returns:
            CustomUser: Созданный пользователь

        Raises:
            ValueError: Если имя пользователя не указано
        """
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Создание суперпользователя.

        Parameters:
            username (str): Имя пользователя
            password (str): Пароль пользователя
            **extra_fields: Дополнительные поля

        Returns:
            CustomUser: Созданный суперпользователь

        Raises:
            ValueError: Если обязательные поля не установлены
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_level', 3)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser, UUIDMixin):
    """Модель пользователя с дополнительными полями и ролями."""

    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    USER_LEVEL_CHOICES = [
        (0, 'Patient'),
        (1, 'Doctor'),
        (2, 'Admin'),
        (3, 'Superuser'),
    ]
    user_level = models.SmallIntegerField(choices=USER_LEVEL_CHOICES, default=0)

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Visit(UUIDMixin):
    """Модель визита к врачу."""

    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_visits')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_visits')
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.date} - {self.doctor.fullname} with {self.patient.fullname}'

    class Meta:
        permissions = [
            ('can_view_visit', 'Can view visit'),
            ('can_edit_visit', 'Can edit visit'),
        ]
        verbose_name = 'Визит'
        verbose_name_plural = 'Визиты'


class Schedule(UUIDMixin):
    """Модель расписания доктора."""

    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_schedule')
    start = models.TimeField()
    end = models.TimeField()
    DAY_OF_WEEK_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    day_of_week = models.SmallIntegerField(choices=DAY_OF_WEEK_CHOICES)

    def __str__(self) -> str:
        return f'{self.doctor.fullname} - {self.get_day_of_week_display()}'

    class Meta:
        permissions = [
            ('can_view_schedule', 'Can view schedule'),
            ('can_edit_schedule', 'Can edit schedule'),
        ]
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'


class Diagnosis(UUIDMixin):
    """Модель диагноза пациента."""

    description = models.TextField(blank=True, null=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_diagnoses')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_diagnoses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.patient.fullname} - {self.description}'

    class Meta:
        permissions = [
            ('can_view_diagnosis', 'Can view diagnosis'),
            ('can_edit_diagnosis', 'Can edit diagnosis'),
        ]
        verbose_name = 'Диагноз'
        verbose_name_plural = 'Диагнозы'
