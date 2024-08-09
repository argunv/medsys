from clinic.config.models import FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH
from clinic.validators.models import (validate_first_name, validate_last_name,
                                      validate_specialty)
from django.core.exceptions import ValidationError
from django.test import TestCase


class ValidatorsModelsTest(TestCase):

    def test_validate_first_name_success(self):
        name = "John"
        self.assertEqual(validate_first_name(name), name)

    def test_validate_first_name_required(self):
        with self.assertRaises(ValidationError) as cm:
            validate_first_name("")
        self.assertEqual(str(cm.exception), "['First name is required.']")

    def test_validate_first_name_format(self):
        with self.assertRaises(ValidationError) as cm:
            validate_first_name("John123")
        self.assertEqual(str(cm.exception), "['First name must contain only letters.']")

    def test_validate_first_name_length(self):
        long_name = "J" * (FIRST_NAME_MAX_LENGTH + 1)
        with self.assertRaises(ValidationError) as cm:
            validate_first_name(long_name)
        self.assertEqual(str(cm.exception), f"['First name cannot be longer than {FIRST_NAME_MAX_LENGTH} characters.']")

    def test_validate_last_name_success(self):
        name = "Doe"
        self.assertEqual(validate_last_name(name), name)

    def test_validate_last_name_required(self):
        with self.assertRaises(ValidationError) as cm:
            validate_last_name("")
        self.assertEqual(str(cm.exception), "['Last name is required.']")

    def test_validate_last_name_format(self):
        with self.assertRaises(ValidationError) as cm:
            validate_last_name("Doe123")
        self.assertEqual(str(cm.exception), "['Last name must contain only letters.']")

    def test_validate_last_name_length(self):
        long_name = "D" * (LAST_NAME_MAX_LENGTH + 1)
        with self.assertRaises(ValidationError) as cm:
            validate_last_name(long_name)
        self.assertEqual(str(cm.exception), f"['Last name cannot be longer than {LAST_NAME_MAX_LENGTH} characters.']")

    def test_validate_specialty_success(self):
        specialization = "Cardiology"
        self.assertEqual(validate_specialty(specialization), specialization)

    def test_validate_specialty_format(self):
        with self.assertRaises(ValidationError) as cm:
            validate_specialty("Cardiology123")
        self.assertEqual(str(cm.exception), "['Specialization must contain only letters.']")

