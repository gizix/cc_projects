"""
Custom validators for data validation.

Provides reusable validation functions.
"""

import re
from typing import Tuple


def validate_email_format(email: str) -> Tuple[bool, str]:
    """
    Validate email format.

    Args:
        email (str): Email address to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, 'Invalid email format'

    return True, ''


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password (str): Password to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'

    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit'

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password must contain at least one special character'

    return True, ''


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.

    Requirements:
    - 3-80 characters
    - Only letters, numbers, and underscores
    - Must start with a letter

    Args:
        username (str): Username to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, 'Username must be at least 3 characters long'

    if len(username) > 80:
        return False, 'Username must be at most 80 characters long'

    if not username[0].isalpha():
        return False, 'Username must start with a letter'

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers, and underscores'

    return True, ''
