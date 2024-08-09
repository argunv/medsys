"""Serializers for the clinic app."""
from rest_framework.serializers import ModelSerializer, SlugRelatedField

from .config.fields import SERIALIZER_FIELDS
from .config.levels import UserLevel
from .config.strings import STR_USERNAME
from .models import (CustomUser, Diagnosis, DoctorSpecialization, Schedule,
                     Visit)


class CustomUserSerializer(ModelSerializer):
    """
    Serializer for the CustomUser model.

    Attributes:
        groups (PrimaryKeyRelatedField): A field that represents the groups associated with the user.
        user_permissions (PrimaryKeyRelatedField): A field that represents the permissions associated with the user.

    Meta:
        model (CustomUser): The model class that the serializer is based on.
        fields (tuple[str]): The fields to include in the serialized representation.
    """

    class Meta:
        """Meta options for the CustomUserSerializer."""

        model = CustomUser
        fields: tuple[str] = SERIALIZER_FIELDS['User']


class VisitSerializer(ModelSerializer):
    """
    Serializer for the Visit model.

    Attributes:
        doctor (SlugRelatedField): A field that represents the doctor associated with the visit.
        patient (SlugRelatedField): A field that represents the patient associated with the visit.

    Meta:
        model (Visit): The model class that the serializer is based on.
        fields (tuple[str]): The fields to include in the serialized representation
    """

    doctor: SlugRelatedField = SlugRelatedField(
        slug_field=STR_USERNAME,
        queryset=CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value))
    patient: SlugRelatedField = SlugRelatedField(
        slug_field=STR_USERNAME,
        queryset=CustomUser.objects.filter(user_level=UserLevel.PATIENT.value))

    class Meta:
        """Meta options for the VisitSerializer."""

        model = Visit
        fields: tuple[str] = SERIALIZER_FIELDS['Visit']


class ScheduleSerializer(ModelSerializer):
    """
    Serializer for the Schedule model.

    Attributes:
        doctor (SlugRelatedField): A field that represents the doctor associated with the schedule.

    Meta:
        model (Schedule): The model class that the serializer is based on.
        fields (tuple[str]): The fields to include in the serialized representation.
    """

    doctor: SlugRelatedField = SlugRelatedField(slug_field=STR_USERNAME,
                                                queryset=CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value))

    class Meta:
        """Meta options for the ScheduleSerializer."""

        model = Schedule
        fields: tuple[str] = SERIALIZER_FIELDS['Schedule']


class DiagnosisSerializer(ModelSerializer):
    """
    Serializer for the Diagnosis model.

    Attributes:
        doctor (SlugRelatedField): A field that represents the doctor associated with the diagnosis.
        patient (SlugRelatedField): A field that represents the patient associated with the diagnosis.

    Meta:
        model (Diagnosis): The model class that the serializer is based on.
        fields (tuple[str]): The fields to include in the serialized representation.
    """

    doctor: SlugRelatedField = SlugRelatedField(slug_field=STR_USERNAME,
                                                queryset=CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value))
    patient: SlugRelatedField = SlugRelatedField(slug_field=STR_USERNAME,
                                                 queryset=CustomUser.objects.filter(user_level=UserLevel.PATIENT.value))

    class Meta:
        """Meta options for the DiagnosisSerializer."""

        model = Diagnosis
        fields: tuple[str] = SERIALIZER_FIELDS['Diagnosis']


class DoctorSpecializationSerializer(ModelSerializer):
    """
    Serializer for the DoctorSpecialization model.

    Attributes:
        doctor (SlugRelatedField): A field that represents the doctor associated with the specialization.

    Meta:
        model (DoctorSpecialization): The model class that the serializer is based on.
        fields (tuple[str]): The fields to include in the serialized representation.
    """

    doctor: SlugRelatedField = SlugRelatedField(slug_field=STR_USERNAME,
                                                queryset=CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value))

    class Meta:
        """Meta options for the DoctorSpecializationSerializer."""

        model = DoctorSpecialization
        fields: tuple[str] = SERIALIZER_FIELDS['DoctorSpecialization']
