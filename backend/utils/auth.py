"""
Simple authentication utilities.
For Phase 2, we use simple token generation (can be upgraded to JWT later).
"""

import secrets
from typing import Optional
from datetime import datetime, timedelta


def generate_token() -> str:
    """Generate a simple token for player authentication."""
    return secrets.token_urlsafe(32)


def verify_token(token: str) -> bool:
    """
    Verify a token (simple implementation).
    
    In production, this would validate JWT tokens.
    For now, we just check if it's a valid format.
    """
    return len(token) > 0  # Simple check


class PlayerSession:
    """Simple session management for players."""
    
    def __init__(self, player_id: str, room_code: str, token: str):
        self.player_id = player_id
        self.room_code = room_code
        self.token = token
        self.created_at = datetime.now()
    
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        # Sessions valid for 24 hours
        return datetime.now() - self.created_at < timedelta(hours=24)


# In-memory session store (in production, use Redis or database)
_sessions: dict[str, PlayerSession] = {}


def create_session(player_id: str, room_code: str) -> str:
    """
    Create a new player session.
    
    Args:
        player_id: Player ID
        room_code: Room code
        
    Returns:
        Session token
    """
    token = generate_token()
    session = PlayerSession(player_id, room_code, token)
    _sessions[token] = session
    return token


def get_session(token: str) -> Optional[PlayerSession]:
    """Get session by token."""
    session = _sessions.get(token)
    if session and session.is_valid():
        return session
    return None


def validate_player_token(token: str, player_id: str, room_code: str) -> bool:
    """
    Validate that a token belongs to a player in a room.
    
    Args:
        token: Authentication token
        player_id: Player ID
        room_code: Room code
        
    Returns:
        True if token is valid for this player/room
    """
    session = get_session(token)
    if session is None:
        return False
    return session.player_id == player_id and session.room_code == room_code

