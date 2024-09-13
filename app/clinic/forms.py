"""This module contains Django forms used in the clinic application."""
from datetime import datetime

from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.forms import (BooleanField, CharField, DateField, DateInput,
                          EmailField, Form, ModelForm, TimeField, TimeInput,
                          ValidationError)
from phonenumber_field.modelfields import PhoneNumberField
from python_usernames import is_safe_username

from .config.fields import (DATE_ATTRS, DIAGNOSIS_FIELDS, FIELD_IS_ACTIVE,
                            FIELD_USER_LEVEL, MAX_EMAIL_LENGTH,
                            MAX_USERNAME_LENGTH, SCHEDULE_FIELDS,
                            START_END_ATTRS, VISIT_FIELDS)
from .config.levels import UserLevel
from .config.messages import (ERROR_DOCTOR_REQUIRED,
                              ERROR_SEARCH_PARAM_REQUIRED,
                              ERROR_USERNAME_UNSAFE)
from .config.strings import (STR_DATE, STR_DOCTOR, STR_END, STR_HM_FORMAT,
                             STR_PATIENT, STR_START, STR_STATUS)
from .config.user import USER_CHANGE_FIELDS, USER_CREATION_FIELDS
from .models import CustomUser, Diagnosis, Schedule, Visit
from .validators.forms import (validate_doctor_availability,
                               validate_first_name, validate_is_active,
                               validate_last_name, validate_schedule,
                               validate_schedule_existence,
                               validate_specialization, validate_status,
                               validate_time_increment, validate_time_order,
                               validate_user_level)


class VisitForm(ModelForm):
    """
    A form for creating or updating a visit.

    This form includes fields for start time, end time, date, and other related fields.
    It also performs validation to ensure that the visit details are valid and do not conflict with existing visits.

    Attributes:
        start (TimeField): The start time of the visit.
        end (TimeField): The end time of the visit.
        date (DateField): The date of the visit.

    Methods:
        clean() -> dict[str, any]: Performs additional validation and returns the cleaned data.

    Raises:
        ValidationError: If the visit details are invalid or conflict with existing visits.
    """

    start: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))
    end: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))
    date: DateField = DateField(widget=DateInput(format='%Y-%m-%d', attrs=DATE_ATTRS))

    class Meta:
        """Meta class for the VisitForm."""

        model = Visit
        fields = VISIT_FIELDS

    def clean(self) -> dict[str, any]:
        """Clean the form data and perform additional validation.

        Returns:
            dict[str, any]: The cleaned data.
        """
        cleaned_data: dict[str, any] = super().clean()
        start: TimeField = cleaned_data.get(STR_START)
        end: TimeField = cleaned_data.get(STR_END)
        doctor: any = cleaned_data.get(STR_DOCTOR)
        date: DateField = cleaned_data.get(STR_DATE)
        patient: any = cleaned_data.get(STR_PATIENT)
        status: any = cleaned_data.get(STR_STATUS)

        validate_time_order(start, end)
        validate_time_increment(start)
        validate_time_increment(end)
        validate_doctor_availability(doctor, date, start, end, self.instance.id, patient)

        day_of_week: int = date.weekday()
        validate_schedule(doctor, day_of_week, start, end)

        validate_status(status, datetime.combine(date, start), datetime.now())

        return cleaned_data


class ScheduleForm(ModelForm):
    """
    A form for creating or updating a schedule.

    This form includes fields for start time, end time, and other related fields.
    It performs validation to ensure that the schedule details are valid and do not conflict with existing schedules.

    Attributes:
        start (TimeField): The start time of the schedule.
        end (TimeField): The end time of the schedule.

    Methods:
        clean() -> dict[str, any]: Performs additional validation and returns the cleaned data.

    Raises:
        ValidationError: If the schedule details are invalid or conflict with existing schedules.
    """

    start: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))
    end: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))

    class Meta:
        """Meta class for the ScheduleForm."""

        model = Schedule
        fields = SCHEDULE_FIELDS

    def clean(self) -> dict[str, any]:
        """Clean the form data and perform additional validation.

        Returns:
            dict[str, any]: The cleaned data.
        """
        cleaned_data: dict[str, any] = super().clean()
        start: TimeField = cleaned_data.get(STR_START)
        end: TimeField = cleaned_data.get(STR_END)
        doctor: any = cleaned_data.get(STR_DOCTOR)
        day_of_week: any = cleaned_data.get('day_of_week')

        validate_time_order(start, end)
        validate_time_increment(start)
        validate_time_increment(end)
        validate_schedule_existence(doctor, day_of_week, self.instance.id)

        return cleaned_data


class DiagnosisForm(ModelForm):
    """
    A form for creating or updating a diagnosis.

    This form includes fields for description and other related fields.
    It also performs validation to ensure that the diagnosis details are valid.

    Attributes:
        description (CharField): The description of the diagnosis.

    Methods:
        None

    Raises:
        ValidationError: If the diagnosis details are invalid.
    """

    description: CharField = CharField(min_length=10, required=True)

    class Meta:
        """Meta class for the DiagnosisForm."""

        model = Diagnosis
        fields = DIAGNOSIS_FIELDS


class DiagnosisAddForm(DiagnosisForm):
    """
    A form for adding a diagnosis.

    This form inherits from the DiagnosisForm and only includes the description field.
    """

    class Meta:
        """Meta class for the DiagnosisAddForm."""

        model = Diagnosis
        fields = ['description']


class DiagnosisStatusForm(ModelForm):
    """Diagnosis status edit form."""

    is_active: BooleanField = BooleanField(required=False, label='Active')
    description: CharField = CharField(disabled=True, required=False, label='')

    class Meta:
        """Meta class for the DiagnosisStatusForm."""

        model = Diagnosis
        fields = ['is_active', 'description']
        readonly_fields = ['description']


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a user with a level selection."""

    class Meta:
        """Meta class for the CustomUserCreationForm."""

        model = CustomUser
        fields = USER_CREATION_FIELDS

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        validate_user_level(self.request_user, self.instance, self.fields[FIELD_USER_LEVEL])

    def save(self, commit=True) -> CustomUser:
        """
        Save the user instance with specific settings based on user level.

        Args:
            commit (bool): Flag indicating whether to commit the changes.

        Returns:
            CustomUser: The saved user instance.

        Raises:
            ValidationError: If the username is not safe.
        """
        user: CustomUser = super().save(commit=False)
        if user.user_level == UserLevel.DOCTOR.value:
            user.is_active = False
        if user.user_level == UserLevel.ADMIN.value:
            user.is_superuser = True
            user.is_staff = True
            if commit:
                user.save()
                permissions = Permission.objects.all()
                user.user_permissions.set(permissions)
        if not is_safe_username(user.username):
            raise ValidationError(ERROR_USERNAME_UNSAFE)
        if commit:
            user.save()
        return user

    def clean_username(self) -> str:
        """
        Validate the username field.

        Returns:
            str: The cleaned username.

        Raises:
            ValidationError: If the username is not safe.
        """
        username: str = self.cleaned_data.get('username')
        if not is_safe_username(username):
            raise ValidationError(ERROR_USERNAME_UNSAFE)
        return username


class CustomUserChangeForm(UserChangeForm):
    """Form for editing a user with a level selection."""

    class Meta:
        """Meta class for the CustomUserChangeForm."""

        model = CustomUser
        fields = USER_CHANGE_FIELDS

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        if not self.instance:
            return

        self.request_user = getattr(self, 'request_user', None)
        if self.request_user is not None:
            self.fields[FIELD_USER_LEVEL] = validate_user_level(
                self.request_user, self.instance, self.fields[FIELD_USER_LEVEL],
            )

            if self.request_user.user_level == UserLevel.ADMIN.value and self.request_user == self.instance:
                self.fields[FIELD_USER_LEVEL].disabled = True

        self.fields[FIELD_IS_ACTIVE] = validate_is_active(self.instance, self.fields[FIELD_IS_ACTIVE])

    def save(self, commit=True) -> CustomUser:
        """
        Save the user instance with specific settings based on user level.

        Args:
            commit (bool): Flag indicating whether to commit the changes.

        Returns:
            CustomUser: The saved user instance.
        """
        user: CustomUser = super().save(commit=False)

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


class RegisterUserForm(UserCreationForm):
    """Form for registering a new user."""

    class Meta:
        """Meta class for the RegisterUserForm."""

        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')


class ScheduleViewForm(ModelForm):
    """Form for viewing and editing a doctor's schedule."""

    class Meta:
        """Meta class for the ScheduleViewForm."""

        model = Schedule
        fields = ['day_of_week', STR_START, STR_END]

    start: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))
    end: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))

    def __init__(self, *args, **kwargs):
        """Initialize the form with an optional doctor instance.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        self.doctor = kwargs.pop(STR_DOCTOR, None)
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, any]:
        """
        Clean the form data and perform additional validation.

        Returns:
            dict[str, any]: The cleaned data.

        Raises:
            ValidationError: If doctor is not provided or schedule is invalid.
        """
        cleaned_data: dict[str, any] = super().clean()

        doctor: any = self.doctor
        day_of_week: any = cleaned_data.get('day_of_week')

        if not doctor:
            raise ValidationError(ERROR_DOCTOR_REQUIRED)

        validate_schedule_existence(doctor, day_of_week, self.instance.id)
        validate_time_order(cleaned_data[STR_START], cleaned_data[STR_END])
        validate_time_increment(cleaned_data[STR_START])
        validate_time_increment(cleaned_data[STR_END])
        return cleaned_data


class VisitViewForm(ModelForm):
    """Form for viewing visit details."""

    class Meta:
        """Meta class for the VisitViewForm."""

        model = Visit
        fields = [STR_DATE, STR_START, STR_END, STR_STATUS]


class VisitCreationForm(ModelForm):
    """Form for creating a new visit."""

    class Meta:
        """Meta class for the VisitCreationForm."""

        model = Visit
        fields = [STR_DATE, STR_START, STR_END]

    date: DateField = DateField(widget=DateInput(format='%Y-%m-%d', attrs=DATE_ATTRS))
    start: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))
    end: TimeField = TimeField(widget=TimeInput(format=STR_HM_FORMAT, attrs=START_END_ATTRS))

    def __init__(self, *args, **kwargs):
        """Initialize the form with optional doctor and patient instances.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        self.doctor = kwargs.pop(STR_DOCTOR, None)
        self.patient = kwargs.pop(STR_PATIENT, None)
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, any]:
        """
        Clean the form data and perform additional validation.

        Returns:
            dict[str, any]: The cleaned data.

        Exceptions:
            ValidationError: If the visit details are invalid.
        """
        cleaned_data: dict[str, any] = super().clean()
        date: DateField = cleaned_data.get(STR_DATE)
        start: TimeField = cleaned_data.get(STR_START)
        end: TimeField = cleaned_data.get(STR_END)

        validate_time_order(start, end)
        validate_time_increment(start)
        validate_time_increment(end)
        validate_doctor_availability(self.doctor, date, start, end, self.instance.id, self.patient)

        return cleaned_data

    def save(self, commit=True):
        """
        Save the visit with the associated doctor and patient.

        Args:
            commit (bool): Flag indicating whether to commit the changes.

        Returns:
            Visit: The saved visit instance.
        """
        visit: Visit = super().save(commit=False)
        visit.doctor = self.doctor
        visit.patient = self.patient
        if commit:
            visit.save()
        return visit


class VisitUpdateForm(VisitCreationForm):
    """Form for updating an existing visit."""

    class Meta:
        """Meta class for the VisitUpdateForm."""

        model = Visit
        fields = [STR_DATE, STR_START, STR_END, STR_STATUS]

    def __init__(self, *args, **kwargs):
        """Initialize the form with status as an optional field.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.fields[STR_STATUS].required = False


class DoctorSearchForm(Form):
    """Form for searching doctors."""

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

    first_name: CharField = CharField(required=False, label='Имя', validators=[validate_first_name])
    last_name: CharField = CharField(required=False, label='Фамилия', validators=[validate_last_name])
    specialization: CharField = CharField(required=False, label='Специализация', validators=[validate_specialization])
    username: CharField = CharField(max_length=MAX_USERNAME_LENGTH, required=False, label='Имя пользователя')
    email: EmailField = EmailField(max_length=MAX_EMAIL_LENGTH, required=False, label='Email')
    phone: PhoneNumberField = PhoneNumberField()

    def clean(self) -> dict[str, any]:
        """
        Ensure that at least one search parameter is provided.

        Returns:
            dict[str, any]: The cleaned data.

        Raises:
            ValidationError: If no search parameters are provided.
        """
        cleaned_data: dict[str, any] = super().clean()
        for _, cleaned in cleaned_data.items():
            if cleaned != '':
                return cleaned_data
        raise ValidationError(ERROR_SEARCH_PARAM_REQUIRED)
