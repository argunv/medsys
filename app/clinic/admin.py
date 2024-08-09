"""Admin configurations for the clinic app."""

from typing import Optional

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

from .config.fields import FIELD_DATE_JOINED, FIELD_LAST_LOGIN
from .config.levels import UserLevel
from .config.messages import ERROR_IS_ACTIVE, ERROR_SCHEDULE_OVERLAP
from .config.strings import STR_DOCTOR, STR_PATIENT
from .config.user import (USER_ADD_FIELDSETS, USER_FIELDSETS,
                          USER_LIST_DISPLAY, USER_LIST_FILTER,
                          USER_SEARCH_FIELDS)
from .forms import (CustomUserChangeForm, CustomUserCreationForm,
                    DiagnosisForm, ScheduleForm, VisitForm)
from .models import (CustomUser, Diagnosis, DoctorSpecialization, Schedule,
                     Visit)


class CustomUserAdmin(BaseUserAdmin):
    """Custom admin panel for users with levels."""

    class Media:
        """A class that defines the media files (CSS and JS) to be used in the admin interface."""

        css = {
            'all': ('css/intlTelInput.css', 'css/phone.css'),
        }
        js = (
            'js/intlTelInput.js',
            'js/utils.js',
            'js/phone.js',
        )

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = USER_LIST_DISPLAY
    search_fields = USER_SEARCH_FIELDS
    list_filter = USER_LIST_FILTER

    fieldsets = USER_FIELDSETS
    add_fieldsets = USER_ADD_FIELDSETS

    def get_readonly_fields(self, request, user_obj: Optional[CustomUser] = None) -> tuple[str, ...]:
        """
        Return readonly fields based on user level.

        Args:
            request: The HTTP request object.
            user_obj (Optional[CustomUser]): The CustomUser instance.

        Returns:
            tuple[str, ...]: A tuple of readonly field names.
        """
        readonly_fields = (FIELD_LAST_LOGIN, FIELD_DATE_JOINED)
        if request.user.is_superuser:
            return readonly_fields
        if user_obj:
            if user_obj.user_level == UserLevel.SUPERUSER.value:
                return readonly_fields + ('is_superuser', 'is_staff')
            if user_obj.user_level == UserLevel.ADMIN.value:
                return readonly_fields + ('password',)
            if request.user.is_staff:
                return readonly_fields + ('is_superuser',)
        return readonly_fields

    def save_model(self, request, user_obj: CustomUser, form, change: bool) -> None:
        """
        Save the model instance with specific logic based on user level.

        Args:
            request: The HTTP request object.
            user_obj (CustomUser): The CustomUser instance to be saved.
            form: The form instance.
            change (bool): Flag indicating whether the object is being changed.
        """
        if user_obj.user_level != UserLevel.DOCTOR.value and not user_obj.is_active:
            self.message_user(request, ERROR_IS_ACTIVE, level=messages.WARNING)
            user_obj.is_active = True

        if user_obj.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
            user_obj.password = form.initial.get('password', user_obj.password)

        super().save_model(request, user_obj, form, change)

    def has_change_permission(self, request, user_obj: Optional[CustomUser] = None) -> bool:
        """
        Restrict user change permissions based on level.

        Args:
            request: The HTTP request object.
            user_obj (Optional[CustomUser]): The CustomUser instance.

        Returns:
            bool: True if the user has change permission, False otherwise.
        """
        if request.user.is_superuser:
            return True
        if user_obj:
            if user_obj.user_level == UserLevel.SUPERUSER.value:
                return False
            if user_obj.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
                return False
        return super().has_change_permission(request, user_obj)

    def has_delete_permission(self, request, user_obj: Optional[CustomUser] = None) -> bool:
        """
        Restrict user delete permissions based on level.

        Args:
            request: The HTTP request object.
            user_obj (Optional[CustomUser]): The CustomUser instance.

        Returns:
            bool: True if the user has delete permission, False otherwise.
        """
        if request.user.is_superuser:
            return True
        if user_obj:
            if user_obj.user_level == UserLevel.SUPERUSER.value:
                return False
            if user_obj.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
                return False
        return super().has_delete_permission(request, user_obj)

    def has_add_permission(self, request) -> bool:
        """
        Restrict user add permissions based on level.

        Args:
            request: The HTTP request object.

        Returns:
            bool: True if the user has add permission, False otherwise.
        """
        if request.user.is_superuser:
            return True
        return super().has_add_permission(request)

    def get_queryset(self, request) -> QuerySet:
        """
        Restrict user visibility in the queryset based on level.

        Args:
            request: The HTTP request object.

        Returns:
            QuerySet: The filtered queryset.
        """
        queryset = super().get_queryset(request)
        if request.user.user_level == UserLevel.SUPERUSER.value:
            return queryset.exclude(user_level=UserLevel.SUPERUSER.value)
        if request.user.user_level == UserLevel.ADMIN.value:
            return queryset.filter(
                user_level__in=[UserLevel.DOCTOR.value, UserLevel.PATIENT.value],
            )
        return queryset.none()

    def get_form(self, request, user_obj=None, **kwargs):
        """
        Get the form with specific querysets for user levels.

        Args:
            request: The HTTP request object.
            user_obj: The object instance.
            kwargs: Additional keyword arguments.

        Returns:
            form: The form instance with specific querysets.
        """
        form = super().get_form(request, user_obj, **kwargs)
        form.request_user = request.user
        return form


class VisitAdmin(admin.ModelAdmin):
    """Admin panel for managing visits."""

    form = VisitForm
    list_display = (STR_DOCTOR, STR_PATIENT, 'date', 'start', 'end', 'status')
    search_fields = ('doctor__username', 'patient__username', 'date')
    list_filter = ('status', 'date')

    def get_form(self, request, visit_obj=None, **kwargs):
        """
        Get the form with specific querysets for visits.

        Args:
            request: The HTTP request object.
            visit_obj: The object instance.
            kwargs: Additional keyword arguments.

        Returns:
            form: The form instance with specific querysets.
        """
        form = super().get_form(request, visit_obj, **kwargs)
        form.base_fields[STR_DOCTOR].queryset = CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value)
        form.base_fields[STR_PATIENT].queryset = CustomUser.objects.filter(user_level=UserLevel.PATIENT.value)
        return form


class ScheduleAdmin(admin.ModelAdmin):
    """Admin panel for managing schedules."""

    form = ScheduleForm
    list_display = (STR_DOCTOR, 'day_of_week', 'start', 'end')
    search_fields = ('doctor__username',)
    list_filter = ('day_of_week',)

    def get_form(self, request, schedule_obj=None, **kwargs):
        """
        Get the form with specific querysets for schedules.

        Args:
            request: The HTTP request object.
            schedule_obj: The object instance.
            kwargs: Additional keyword arguments.

        Returns:
            form: The form instance with specific querysets.
        """
        form = super().get_form(request, schedule_obj, **kwargs)
        form.base_fields[STR_DOCTOR].queryset = CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value)
        return form

    def save_model(self, request, schedule_obj, form, change):
        """
        Save the schedule instance with validation to prevent overlaps.

        Args:
            request: The HTTP request object.
            schedule_obj: The Schedule instance to be saved.
            form: The form instance.
            change (bool): Flag indicating whether the object is being changed.

        Raises:
            ValidationError: If the schedule overlaps with an existing schedule.
        """
        if self._is_schedule_overlapping(schedule_obj):
            raise ValidationError(ERROR_SCHEDULE_OVERLAP)

        super().save_model(request, schedule_obj, form, change)

    @staticmethod
    def _is_schedule_overlapping(schedule_obj):
        """
        Check if the schedule overlaps with an existing schedule.

        Args:
            schedule_obj: The Schedule instance to be checked.

        Returns:
            bool: True if overlapping, otherwise False.
        """
        overlapping_schedules = Schedule.objects.filter(
            doctor=schedule_obj.doctor,
            day_of_week=schedule_obj.day_of_week,
            start__lt=schedule_obj.end,
            end__gt=schedule_obj.start,
        ).exclude(id=schedule_obj.id)
        return overlapping_schedules.exists()


class DiagnosisAdmin(admin.ModelAdmin):
    """Admin panel for managing diagnoses."""

    form = DiagnosisForm
    list_display = (STR_DOCTOR, STR_PATIENT, 'description', 'is_active')
    search_fields = ('doctor__username', 'patient__username', 'description')
    list_filter = ('is_active',)

    def get_form(self, request, diagnosis_obj=None, **kwargs):
        """
        Get the form with specific querysets for diagnoses.

        Args:
            request: The HTTP request object.
            diagnosis_obj: The object instance.
            kwargs: Additional keyword arguments.

        Returns:
            form: The form instance with specific querysets.
        """
        form = super().get_form(request, diagnosis_obj, **kwargs)
        form.base_fields[STR_DOCTOR].queryset = CustomUser.objects.filter(
            user_level=UserLevel.DOCTOR.value,
            is_active=True,
            )
        form.base_fields[STR_PATIENT].queryset = CustomUser.objects.filter(
            user_level=UserLevel.PATIENT.value,
            )
        return form


class DoctorSpecializationAdmin(admin.ModelAdmin):
    """Admin panel for managing doctor specializations."""

    list_display = (STR_DOCTOR, 'specialization')
    search_fields = (STR_DOCTOR, 'specialization')

    def get_form(self, request, doctor_specialization_obj=None, **kwargs):
        """
        Get the form with specific querysets for doctor specializations.

        Args:
            request: The HTTP request object.
            doctor_specialization_obj: The object instance.
            kwargs: Additional keyword arguments.

        Returns:
            form: The form instance with specific querysets.
        """
        form = super().get_form(request, doctor_specialization_obj, **kwargs)
        form.base_fields[STR_DOCTOR].queryset = CustomUser.objects.filter(
            user_level=UserLevel.DOCTOR.value, is_active=True,
            )
        return form


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Diagnosis, DiagnosisAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(DoctorSpecialization, DoctorSpecializationAdmin)
