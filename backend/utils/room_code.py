"""
Utility functions for generating unique room codes.
"""

import random
import string
from backend.database.db import get_room_by_code


def generate_room_code() -> str:
    """
    Generate a unique 6-character room code (uppercase alphanumeric).
    
    Returns:
        Unique room code string
    """
    chars = string.ascii_uppercase + string.digits
    attempts = 0
    max_attempts = 100
    
    while attempts < max_attempts:
        code = ''.join(random.choice(chars) for _ in range(6))
        # Check if code is unique
        existing_room = get_room_by_code(code)
        if existing_room is None:
            return code
        attempts += 1
    
    raise Exception("Failed to generate unique room code after 100 attempts")


def is_code_unique(code: str) -> bool:
    """
    Check if a room code is unique.
    
    Args:
        code: Room code to check
        
    Returns:
        True if code is unique, False otherwise
    """
    existing_room = get_room_by_code(code)
    return existing_room is None

