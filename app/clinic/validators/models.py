"""Validators for the models of the clinic app."""
from clinic.config.messages import (ERROR_FIRST_NAME_FORMAT,
                                    ERROR_FIRST_NAME_LENGTH,
                                    ERROR_FIRST_NAME_REQUIRED,
                                    ERROR_LAST_NAME_FORMAT,
                                    ERROR_LAST_NAME_LENGTH,
                                    ERROR_LAST_NAME_REQUIRED,
                                    ERROR_SPECIALIZATION_FORMAT)
from clinic.config.models import FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH
from django.core.exceptions import ValidationError


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


def validate_specialty(specialization: str) -> str:
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
