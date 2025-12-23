"""
Room API routes.
Handles room creation, joining, status, and game start.
"""

import uuid
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from backend.models.game import (
    RoomCreateRequest,
    RoomCreateResponse,
    RoomJoinRequest,
    RoomJoinResponse,
    RoomStatusResponse,
    PlayerResponse
)
from backend.database.db import (
    create_room,
    get_room_by_code,
    add_player_to_room,
    get_players_by_room,
    update_room
)
from backend.utils.room_code import generate_room_code
from backend.utils.auth import create_session
from backend.core.game_logic import initialize_game_from_room
from backend.services.bot_service import fill_room_with_bots
from game.core.game import Game

router = APIRouter()


@router.post("/rooms/create", response_model=RoomCreateResponse)
async def create_room_endpoint(request: RoomCreateRequest):
    """
    Create a new game room.
    
    Returns room code and player token.
    """
    # Generate unique room code
    room_code = generate_room_code()
    
    # Create host player
    host_player_id = str(uuid.uuid4())
    
    # Create room in database
    room = create_room(room_code, host_player_id)
    
    # Add host player to room
    add_player_to_room(
        room_code=room_code,
        player_id=host_player_id,
        player_name=request.player_name,
        symbol=request.symbol,
        is_bot=False
    )
    
    # Create session token
    token = create_session(host_player_id, room_code)
    
    return RoomCreateResponse(
        room_code=room_code,
        player_id=host_player_id,
        token=token
    )


@router.post("/rooms/join", response_model=RoomJoinResponse)
async def join_room_endpoint(request: RoomJoinRequest):
    """
    Join an existing room by room code.
    
    Validates symbol uniqueness and adds player to room.
    """
    room = get_room_by_code(request.room_code.upper())
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "waiting":
        raise HTTPException(status_code=400, detail="Room is no longer accepting players")
    
    # Check if symbol is already taken
    existing_players = get_players_by_room(request.room_code)
    for player in existing_players:
        if player.symbol == request.symbol:
            raise HTTPException(status_code=400, detail=f"Symbol '{request.symbol}' is already taken")
    
    # Create new player
    player_id = str(uuid.uuid4())
    
    add_player_to_room(
        room_code=request.room_code.upper(),
        player_id=player_id,
        player_name=request.player_name,
        symbol=request.symbol,
        is_bot=False
    )
    
    # Create session token
    token = create_session(player_id, request.room_code.upper())
    
    return RoomJoinResponse(
        room_code=request.room_code.upper(),
        player_id=player_id,
        token=token
    )


@router.get("/rooms/{room_code}/status", response_model=RoomStatusResponse)
async def get_room_status(room_code: str):
    """Get current status of a room."""
    room = get_room_by_code(room_code.upper())
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    players_db = get_players_by_room(room_code.upper())
    players = [
        PlayerResponse(
            player_id=p.player_id,
            player_name=p.player_name,
            symbol=p.symbol,
            is_bot=p.is_bot,
            joined_at=p.joined_at
        )
        for p in players_db
    ]
    
    return RoomStatusResponse(
        room_code=room.room_code,
        state=room.state,
        players=players,
        host_player_id=room.host_player_id,
        created_at=room.created_at,
        started_at=room.started_at,
        finished_at=room.finished_at,
        winner_player_id=room.winner_player_id
    )


@router.post("/rooms/{room_code}/start")
async def start_room_game(room_code: str):
    """
    Start the game for a room.
    
    Automatically fills with bots if less than 5 players.
    Ensures minimum 4 players.
    """
    room = get_room_by_code(room_code.upper())
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "waiting":
        raise HTTPException(status_code=400, detail="Game already started or finished")
    
    players = get_players_by_room(room_code.upper())
    
    # Ensure minimum 4 players
    if len(players) < Game.MIN_PLAYERS:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {Game.MIN_PLAYERS} players to start. Current: {len(players)}"
        )
    
    # Fill with bots to reach 5 players (optional, can be made configurable)
    if len(players) < 5:
        bots_added = fill_room_with_bots(room_code.upper(), target_count=5)
        if bots_added > 0:
            players = get_players_by_room(room_code.upper())  # Refresh player list
    
    # Initialize game
    try:
        initialize_game_from_room(room_code.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize game: {str(e)}")
    
    # Update room state
    update_room(
        room_code.upper(),
        state="playing",
        started_at=datetime.utcnow()
    )
    
    return {
        "success": True,
        "message": "Game started",
        "room_code": room_code.upper(),
        "players": len(players)
    }


@router.get("/rooms/{room_code}/board")
async def get_room_board(room_code: str):
    """Get current board state for a room."""
    from backend.core.game_logic import get_game_state_from_room
    
    try:
        game_state = get_game_state_from_room(room_code.upper())
        return game_state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

