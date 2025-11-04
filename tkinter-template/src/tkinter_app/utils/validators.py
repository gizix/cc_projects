"""Form validation utilities."""

import re
from typing import Callable


class FormValidator:
    """Collection of validation functions for form inputs."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        # Remove common separators
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        pattern = r"^\+?1?\d{9,15}$"
        return bool(re.match(pattern, cleaned))

    @staticmethod
    def validate_not_empty(value: str) -> bool:
        """Validate that value is not empty.

        Args:
            value: Value to validate

        Returns:
            True if not empty, False otherwise
        """
        return bool(value and value.strip())

    @staticmethod
    def validate_length(
        value: str, min_length: int = 0, max_length: int | None = None
    ) -> bool:
        """Validate string length.

        Args:
            value: Value to validate
            min_length: Minimum length
            max_length: Maximum length (None for no limit)

        Returns:
            True if length is valid, False otherwise
        """
        length = len(value)
        if length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True

    @staticmethod
    def validate_number(value: str, allow_float: bool = False) -> bool:
        """Validate that value is a number.

        Args:
            value: Value to validate
            allow_float: Whether to allow floating point numbers

        Returns:
            True if valid number, False otherwise
        """
        if not value:
            return False
        try:
            if allow_float:
                float(value)
            else:
                int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_range(
        value: str,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> bool:
        """Validate that number is within range.

        Args:
            value: Value to validate
            min_val: Minimum value (None for no minimum)
            max_val: Maximum value (None for no maximum)

        Returns:
            True if within range, False otherwise
        """
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_pattern(value: str, pattern: str) -> bool:
        """Validate value against regex pattern.

        Args:
            value: Value to validate
            pattern: Regex pattern

        Returns:
            True if matches pattern, False otherwise
        """
        return bool(re.match(pattern, value))

    @classmethod
    def validate_form(
        cls, data: dict[str, str], rules: dict[str, list[Callable[[str], bool]]]
    ) -> tuple[bool, list[str]]:
        """Validate entire form using rules.

        Args:
            data: Form data dictionary
            rules: Validation rules dictionary mapping field names to validator functions

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for field, validators in rules.items():
            value = data.get(field, "")
            for validator in validators:
                if not validator(value):
                    errors.append(f"Invalid {field}")
                    break

        return len(errors) == 0, errors


def create_tk_validator(
    validator_func: Callable[[str], bool]
) -> Callable[[str], bool]:
    """Create Tkinter-compatible validator function.

    Args:
        validator_func: Validation function

    Returns:
        Tkinter-compatible validator
    """

    def tk_validator(new_value: str) -> bool:
        """Tkinter validator wrapper.

        Args:
            new_value: New entry value

        Returns:
            True if valid, False otherwise
        """
        if new_value == "":
            return True
        return validator_func(new_value)

    return tk_validator
