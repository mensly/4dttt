"""
Game API routes.
Handles move submission, game state retrieval, and move history.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from backend.models.game import MoveRequest, MoveResponse, GameStateResponse
from backend.core.game_logic import process_move, get_game_state_from_room
from backend.utils.auth import validate_player_token
from backend.database.db import get_room_by_code, get_moves_by_room, get_player_by_id
from backend.services.bot_service import execute_bot_move_if_needed

router = APIRouter()


@router.post("/game/{room_code}/move", response_model=MoveResponse)
async def submit_move(
    room_code: str,
    move: MoveRequest,
    player_id: str = Header(..., alias="X-Player-ID"),
    token: str = Header(..., alias="Authorization")
):
    """
    Submit a move.
    
    Requires player_id and token in headers.
    """
    # Validate token
    if not validate_player_token(token.replace("Bearer ", ""), player_id, room_code.upper()):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Verify room exists
    room = get_room_by_code(room_code.upper())
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.state != "playing":
        raise HTTPException(status_code=400, detail="Game is not in playing state")
    
    # Process the move
    success, error, game_info = process_move(
        room_code.upper(),
        player_id,
        move.w, move.x, move.y, move.z
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Invalid move")
    
    # If game continues and next player is a bot, execute bot move asynchronously
    # For now, we'll handle it synchronously but could use background tasks
    if game_info.get('state') == 'playing':
        try:
            from backend.core.game_logic import initialize_game_from_room
            game = initialize_game_from_room(room_code.upper())
            execute_bot_move_if_needed(room_code.upper(), game)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error executing bot move: {e}")
    
    return MoveResponse(
        success=True,
        error=None,
        game_state=game_info.get('state', 'playing'),
        winner=game_info.get('winner')
    )


@router.get("/game/{room_code}/state", response_model=GameStateResponse)
async def get_game_state(room_code: str):
    """Get current game state."""
    try:
        game_state = get_game_state_from_room(room_code.upper())
        return GameStateResponse(**game_state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/game/{room_code}/history")
async def get_move_history(room_code: str):
    """Get move history for a room."""
    room = get_room_by_code(room_code.upper())
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    moves_db = get_moves_by_room(room_code.upper())
    
    return {
        "room_code": room_code.upper(),
        "moves": [
            {
                "move_id": m.move_id,
                "player_id": m.player_id,
                "move": [m.w, m.x, m.y, m.z],
                "move_number": m.move_number,
                "created_at": m.created_at.isoformat()
            }
            for m in moves_db
        ],
        "total_moves": len(moves_db)
    }

