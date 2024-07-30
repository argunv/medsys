"""Admin configurations for the clinic app."""

from typing import Optional

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.db.models.query import QuerySet

from .config.fields import (FIELD_DATE_JOINED, FIELD_IS_ACTIVE,
                            FIELD_LAST_LOGIN, FIELD_USER_LEVEL)
from .config.messages import (CONFIRM_SELECTED_DOCTORS,
                              ERROR_SUPERUSER_ASSIGNMENT,
                              ERROR_SUPERUSER_CREATION,
                              REJECT_SELECTED_DOCTORS, SUCCESSFULLY_UNVERIFIED,
                              SUCCESSFULLY_VERIFIED)
from .config.user import (USER_ADD_FIELDSETS, USER_CHANGE_FIELDS,
                          USER_CREATION_FIELDS, USER_FIELDSETS,
                          USER_LIST_DISPLAY, USER_LIST_FILTER,
                          USER_SEARCH_FIELDS, UserLevel)
from .models import CustomUser, Diagnosis, Schedule, Visit


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a user with a level selection."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = USER_CREATION_FIELDS

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_level == UserLevel.SUPERUSER.value:
            self.fields[FIELD_USER_LEVEL].disabled = True

        self.fields[FIELD_USER_LEVEL].choices = [
            (level.value, level.name) for level in UserLevel if level != UserLevel.SUPERUSER
        ]

    def save(self, commit=True) -> CustomUser:
        """
        Save the user instance with specific settings based on user level.

        Parameters:
            commit (bool): Flag indicating whether to commit the changes.

        Returns:
            CustomUser: The saved user instance.
        """
        user = super().save(commit=False)
        if user.user_level == UserLevel.DOCTOR.value:
            user.is_active = False
        if user.user_level == UserLevel.ADMIN.value:
            user.is_superuser = True
            user.is_staff = True
            if commit:
                user.save()
                permissions = Permission.objects.all()
                user.user_permissions.set(permissions)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Form for editing a user with a level selection."""

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = USER_CHANGE_FIELDS

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        user = kwargs.get('initial', {}).get('user')
        if not self.instance:
            return
        if self.instance.user_level == UserLevel.SUPERUSER.value:
            self.fields[FIELD_USER_LEVEL].disabled = True
        if user and user.user_level == UserLevel.ADMIN.value:
            self.fields[FIELD_USER_LEVEL].choices = [
                (level.value, level.name) for level in UserLevel if level != UserLevel.SUPERUSER
            ]
        if user and user.user_level == UserLevel.ADMIN.value and user == self.instance:
            self.fields[FIELD_USER_LEVEL].disabled = True
        if user and not user.is_superuser and self.instance.is_superuser:
            self.fields[FIELD_USER_LEVEL].disabled = True
        if user and not user.is_superuser:
            self.fields['is_superuser'].disabled = True
            self.fields['is_staff'].disabled = True
        if self.instance.user_level != UserLevel.DOCTOR.value:
            self.fields[FIELD_IS_ACTIVE].disabled = True


class CustomUserAdmin(BaseUserAdmin):
    """Custom admin panel for users with levels."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = USER_LIST_DISPLAY
    search_fields = USER_SEARCH_FIELDS
    list_filter = USER_LIST_FILTER

    fieldsets = USER_FIELDSETS

    add_fieldsets = USER_ADD_FIELDSETS

    def get_readonly_fields(self, request, object: Optional[CustomUser] = None) -> tuple[str, ...]:
        """
        Return readonly fields based on user level.

        Parameters:
            request: The HTTP request object.
            object (Optional[CustomUser]): The CustomUser instance.

        Returns:
            tuple[str, ...]: A tuple of readonly field names.
        """
        readonly_fields = (FIELD_LAST_LOGIN, FIELD_DATE_JOINED)
        if request.user.is_superuser:
            return readonly_fields
        if object:
            if object.user_level == UserLevel.SUPERUSER.value:
                return readonly_fields + ('is_superuser', 'is_staff')
            if object.user_level == UserLevel.ADMIN.value:
                return readonly_fields + ('password',)
            if request.user.is_staff:
                return readonly_fields + ('is_superuser',)
        return readonly_fields

    def save_model(self, request, obj: CustomUser, form, change: bool) -> None:
        """
        Save the model instance with specific logic based on user level.

        Parameters:
            request: The HTTP request object.
            object (CustomUser): The CustomUser instance to be saved.
            form: The form instance.
            change (bool): Flag indicating whether the object is being changed.
        """
        if object.user_level == UserLevel.SUPERUSER.value:
            object.is_superuser = True
            object.is_staff = True
        elif object.user_level == UserLevel.ADMIN.value:
            object.is_staff = True
        else:
            object.is_superuser = False
            object.is_staff = False

        if object.user_level == UserLevel.SUPERUSER.value and not request.user.is_superuser:
            self.message_user(request, ERROR_SUPERUSER_CREATION, level=messages.ERROR)
            return

        if not request.user.is_superuser and object.is_superuser:
            self.message_user(request, ERROR_SUPERUSER_ASSIGNMENT, level=messages.ERROR)
            return

        if object.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
            object.password = form.initial.get('password', object.password)

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, object: Optional[CustomUser] = None) -> bool:
        """
        Restrict user change permissions based on level.

        Parameters:
            request: The HTTP request object.
            object (Optional[CustomUser]): The CustomUser instance.

        Returns:
            bool: True if the user has change permission, False otherwise.
        """
        if request.user.is_superuser:
            return True
        if object:
            if object.user_level == UserLevel.SUPERUSER.value:
                return False
            if object.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
                return False
        return super().has_change_permission(request, object)

    def has_delete_permission(self, request, object: Optional[CustomUser] = None) -> bool:
        """
        Restrict user delete permissions based on level.

        Parameters:
            request: The HTTP request object.
            object (Optional[CustomUser]): The CustomUser instance.

        Returns:
            bool: True if the user has delete permission, False otherwise.
        """
        if request.user.is_superuser:
            return True
        if object:
            if object.user_level == UserLevel.SUPERUSER.value:
                return False
            if object.user_level == UserLevel.ADMIN.value and not request.user.is_superuser:
                return False
        return super().has_delete_permission(request, object)

    def has_add_permission(self, request) -> bool:
        """
        Restrict user add permissions based on level.

        Parameters:
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

        Parameters:
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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Diagnosis)
admin.site.register(Schedule)
admin.site.register(Visit)
