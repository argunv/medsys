"""Module for handling signals related to user groups and visit status updates."""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import CustomUser, Diagnosis, Schedule, Visit

FIFTEEN_MINUTES = 15


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """Signal to create user groups and set their permissions after migrations.

    Args:
        sender: The sender of the signal.
        kwargs: Additional arguments.
    """
    # Creating groups
    patient_group, _ = Group.objects.get_or_create(name='Patients')
    doctor_group, _ = Group.objects.get_or_create(name='Doctors')
    admin_group, _ = Group.objects.get_or_create(name='Admins')

    # Getting permissions
    user_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(CustomUser),
    )
    visit_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Visit),
    )
    schedule_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Schedule),
    )
    diagnosis_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Diagnosis),
    )

    # Setting permissions
    patient_group.permissions.set(
        visit_permissions | diagnosis_permissions,
    )
    doctor_group.permissions.set(
        visit_permissions | schedule_permissions | diagnosis_permissions,
    )
    admin_group.permissions.set(
        user_permissions | visit_permissions | schedule_permissions | diagnosis_permissions,
    )

    # Superusers group
    superuser_group, _ = Group.objects.get_or_create(name='Superusers')
    superuser_group.permissions.set(Permission.objects.all())
