from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from .models import CustomUser, Visit, Schedule, Diagnosis


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Создаем группы
    patient_group, created = Group.objects.get_or_create(name='Patients')
    doctor_group, created = Group.objects.get_or_create(name='Doctors')
    admin_group, created = Group.objects.get_or_create(name='Admins')

    # Получаем разрешения для каждой модели
    user_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(CustomUser))
    visit_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Visit))
    schedule_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Schedule))
    diagnosis_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Diagnosis))

    # Назначаем разрешения группам
    patient_group.permissions.set(visit_permissions | diagnosis_permissions)
    doctor_group.permissions.set(visit_permissions | schedule_permissions | diagnosis_permissions)
    admin_group.permissions.set(user_permissions | visit_permissions | schedule_permissions | diagnosis_permissions)

    # Суперпользовательская группа
    superuser_group, created = Group.objects.get_or_create(name='Superusers')
    superuser_group.permissions.set(Permission.objects.all())
