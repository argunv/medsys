from enum import Enum


class UserLevel(Enum):
    """Enumeration of user levels."""
    SUPERUSER = 3
    ADMIN = 2
    DOCTOR = 1
    PATIENT = 0

    @classmethod
    def choices(cls) -> list:
        """Return the choices for the user level.

        Returns:
            list: The list of choices for the user level.
        """
        return [(level.value, level.name) for level in cls]


class UserLimitChoices:
    """Enumeration of user limit choices."""
    DOCTOR = {'user_level': UserLevel.DOCTOR.value, 'is_active': True}
    PATIENT = {'user_level': UserLevel.PATIENT.value, 'is_active': True}
    ADMIN = {'user_level': UserLevel.ADMIN.value, 'is_active': True}
    SUPERUSER = {'user_level': UserLevel.SUPERUSER.value, 'is_active': True}


ROLES = {'patient': 0, 'doctor': 1, 'admin': 2, 'superuser': 3}