"""
Pydantic models for game API requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PlayerResponse(BaseModel):
    """Player information in API responses."""
    player_id: str
    player_name: str
    symbol: str
    is_bot: bool
    joined_at: datetime


class RoomCreateRequest(BaseModel):
    """Request to create a new room."""
    player_name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=2, description="Player symbol (1-2 characters)")


class RoomCreateResponse(BaseModel):
    """Response when creating a room."""
    room_code: str
    player_id: str
    token: str  # JWT token for authentication


class RoomJoinRequest(BaseModel):
    """Request to join a room."""
    room_code: str = Field(..., min_length=6, max_length=6)
    player_name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=2, description="Player symbol (1-2 characters)")


class RoomJoinResponse(BaseModel):
    """Response when joining a room."""
    room_code: str
    player_id: str
    token: str  # JWT token for authentication


class RoomStatusResponse(BaseModel):
    """Room status response."""
    room_code: str
    state: str  # "waiting", "playing", "finished"
    players: List[PlayerResponse]
    host_player_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    winner_player_id: Optional[str] = None


class MoveRequest(BaseModel):
    """Request to make a move."""
    w: int = Field(..., ge=0, le=2, description="W coordinate (0-2)")
    x: int = Field(..., ge=0, le=2, description="X coordinate (0-2)")
    y: int = Field(..., ge=0, le=2, description="Y coordinate (0-2)")
    z: int = Field(..., ge=0, le=2, description="Z coordinate (0-2)")


class MoveResponse(BaseModel):
    """Response after making a move."""
    success: bool
    error: Optional[str] = None
    game_state: str  # "playing", "finished"
    winner: Optional[str] = None  # Player ID if game finished with a winner


class GameStateResponse(BaseModel):
    """Current game state response."""
    room_code: str
    state: str  # "waiting", "playing", "finished"
    current_player_id: Optional[str] = None
    board_state: List[List[List[List[Optional[str]]]]]  # 4D board representation
    move_count: int
    winner_player_id: Optional[str] = None
    is_draw: bool
    players: Optional[List[PlayerResponse]] = None

