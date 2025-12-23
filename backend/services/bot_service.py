"""
Bot service for automatically filling rooms and executing bot moves.
"""

import sys
import uuid
from typing import Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from game.core.game import Game
from game.ai.simple_ai import SimpleAI
from game.ai.minimax_ai import MinimaxAI
from backend.database.db import add_player_to_room, get_players_by_room, get_room_by_code
from backend.core.game_logic import initialize_game_from_room, process_move


def fill_room_with_bots(room_code: str, target_count: int = 5) -> int:
    """
    Fill a room with AI bots to reach target player count.
    
    Args:
        room_code: Room code
        target_count: Target number of players (default 5, max)
        
    Returns:
        Number of bots added
    """
    room = get_room_by_code(room_code)
    if room is None:
        return 0
    
    if room.state != "waiting":
        return 0  # Can only add bots while waiting
    
    current_players = get_players_by_room(room_code)
    current_count = len(current_players)
    
    if current_count >= target_count:
        return 0
    
    bots_added = 0
    bot_symbols = ['🤖', '⚙️', '🎮', '🧠', '⭐']  # Emoji symbols for bots
    used_symbols = {p.symbol for p in current_players}
    
    for i in range(target_count - current_count):
        # Find an available symbol
        bot_symbol = None
        for symbol in bot_symbols:
            if symbol not in used_symbols:
                bot_symbol = symbol
                used_symbols.add(symbol)
                break
        
        if bot_symbol is None:
            # Fallback to letter symbols
            for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                symbol = f"B{char}"  # Bot prefix
                if symbol not in used_symbols:
                    bot_symbol = symbol
                    used_symbols.add(symbol)
                    break
        
        if bot_symbol is None:
            break  # No available symbols
        
        bot_id = str(uuid.uuid4())
        bot_name = f"Bot-{bots_added + 1}"
        
        add_player_to_room(
            room_code=room_code,
            player_id=bot_id,
            player_name=bot_name,
            symbol=bot_symbol,
            is_bot=True
        )
        
        bots_added += 1
    
    return bots_added


def execute_bot_move_if_needed(room_code: str, game: Optional[Game] = None) -> bool:
    """
    Execute a bot move if the current player is a bot.
    
    Args:
        room_code: Room code
        game: Optional game instance (will be loaded if not provided)
        
    Returns:
        True if a bot move was executed, False otherwise
    """
    if game is None:
        game = initialize_game_from_room(room_code)
    
    if game.state.value != "playing":
        return False
    
    current_player = game.get_current_player()
    if current_player is None or not current_player.is_bot:
        return False
    
    # Create AI instance for bot
    # Use SimpleAI for now (can be made configurable)
    ai = SimpleAI(current_player.symbol, current_player.player_name)
    
    # Get move from AI
    try:
        board = game.get_board_copy()
        w, x, y, z = ai.get_move(board)
        
        # Process the move
        success, error, game_info = process_move(room_code, current_player.player_id, w, x, y, z)
        
        if success:
            # If game continues and next player is also a bot, execute recursively
            # But limit depth to avoid infinite loops
            if game_info.get('state') == 'playing':
                # Small delay would be nice but we'll skip for now
                pass
        
        return success
    except Exception as e:
        print(f"Error executing bot move: {e}")
        return False

