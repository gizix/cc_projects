"""User schemas."""
from dataclasses import dataclass

@dataclass
class UserResponse:
    """User response schema."""
    id: int
    username: str
    email: str
    created_at: str
