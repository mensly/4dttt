"""
Core game logic integration with Phase 1 game module.
Wraps the Phase 1 game logic for web API use.
"""

import sys
import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

# Add project root to path to import game module
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from game.core.game import Game, GameState, Player
from game.core.board import Board
from backend.database.db import get_room_by_code, get_players_by_room, get_moves_by_room, update_room


# In-memory game instances (keyed by room_code)
_active_games: Dict[str, Game] = {}


def initialize_game_from_room(room_code: str) -> Game:
    """
    Initialize a Game instance from a room in the database.
    
    Args:
        room_code: Room code
        
    Returns:
        Initialized Game instance
    """
    # Check if game already exists in memory
    if room_code in _active_games:
        return _active_games[room_code]
    
    # Get room and players from database
    room_db = get_room_by_code(room_code)
    if room_db is None:
        raise ValueError(f"Room {room_code} not found")
    
    players_db = get_players_by_room(room_code)
    if len(players_db) < Game.MIN_PLAYERS:
        raise ValueError(f"Room {room_code} has insufficient players")
    
    # Create game instance
    game = Game()
    
    # Add players
    for player_db in players_db:
        game.add_player(
            player_db.player_id,
            player_db.player_name,
            player_db.symbol,
            is_bot=player_db.is_bot
        )
    
    # Reconstruct board state from moves if game is in progress
    if room_db.state == "playing" and room_db.board_state:
        # Load board state from database
        board_state = room_db.board_state
        board = game.board
        for w in range(3):
            for x in range(3):
                for y in range(3):
                    for z in range(3):
                        symbol = board_state[w][x][y][z]
                        if symbol:
                            board.set(w, x, y, z, symbol)
    elif room_db.state == "playing":
        # Reconstruct from moves
        moves_db = get_moves_by_room(room_code)
        board = game.board
        for move_db in moves_db:
            symbol = next((p.symbol for p in game.players if p.player_id == move_db.player_id), None)
            if symbol:
                board.set(move_db.w, move_db.x, move_db.y, move_db.z, symbol)
    
    # Set game state
    if room_db.state == "playing":
        game.state = GameState.PLAYING
        # Determine current player from move count
        move_count = len(get_moves_by_room(room_code))
        if move_count > 0:
            game.current_player_index = move_count % len(game.players)
        else:
            game.current_player_index = 0
    elif room_db.state == "finished":
        game.state = GameState.FINISHED
        if room_db.winner_player_id:
            game.winner = next((p for p in game.players if p.player_id == room_db.winner_player_id), None)
    
    # Store game in memory
    _active_games[room_code] = game
    
    return game


def process_move(room_code: str, player_id: str, w: int, x: int, y: int, z: int) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Process a move for a room.
    
    Args:
        room_code: Room code
        player_id: Player ID making the move
        w, x, y, z: Move coordinates
        
    Returns:
        Tuple of (success, error_message, game_info)
    """
    game = initialize_game_from_room(room_code)
    
    # Make the move
    success, error = game.make_move(player_id, w, x, y, z)
    
    if not success:
        return False, error, {}
    
    # Save move to database
    from backend.database.db import save_move
    move_count = len(game.move_history)
    save_move(room_code, player_id, w, x, y, z, move_count)
    
    # Update room state
    game_info = {
        'state': game.state.value,
        'winner': game.winner.player_id if game.winner else None,
        'is_draw': game.check_game_over() and game.winner is None
    }
    
    # Update database
    from datetime import datetime
    if game.state == GameState.FINISHED:
        update_room(
            room_code,
            state="finished",
            finished_at=datetime.utcnow(),
            winner_player_id=game.winner.player_id if game.winner else None,
            board_state=game.board.get_board_state()
        )
    else:
        update_room(
            room_code,
            board_state=game.board.get_board_state()
        )
    
    # Note: Bot moves are handled asynchronously in the API layer
    # to avoid blocking the request
    
    return True, None, game_info


def get_game_state_from_room(room_code: str) -> Dict[str, Any]:
    """
    Get current game state for a room.
    
    Args:
        room_code: Room code
        
    Returns:
        Dictionary with game state information
    """
    game = initialize_game_from_room(room_code)
    
    return {
        'room_code': room_code,
        'state': game.state.value,
        'current_player_id': game.get_current_player().player_id if game.get_current_player() else None,
        'board_state': game.board.get_board_state(),
        'move_count': len(game.move_history),
        'winner_player_id': game.winner.player_id if game.winner else None,
        'is_draw': game.check_game_over() and game.winner is None
    }

