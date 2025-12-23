"""
Game state management for 4D Tic-Tac-Toe.
Handles game flow, turn management, and player management.
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
from .board import Board
from .win_checker import get_win_checker


class GameState(Enum):
    """Game state enumeration."""
    WAITING = "waiting"      # Waiting for players
    PLAYING = "playing"      # Game in progress
    FINISHED = "finished"    # Game completed


class Player:
    """Represents a player in the game."""
    
    def __init__(self, player_id: str, player_name: str, symbol: str, is_bot: bool = False):
        """
        Initialize a player.
        
        Args:
            player_id: Unique player identifier
            player_name: Display name
            symbol: Player symbol (1-2 characters)
            is_bot: Whether this is an AI bot
        """
        self.player_id = player_id
        self.player_name = player_name
        self.symbol = symbol
        self.is_bot = is_bot
    
    def __repr__(self):
        return f"Player(id={self.player_id}, name={self.player_name}, symbol={self.symbol}, bot={self.is_bot})"


class Game:
    """Manages the game state and flow."""
    
    MIN_PLAYERS = 4
    MAX_PLAYERS = 5
    
    def __init__(self):
        """Initialize a new game."""
        self.board = Board()
        self.win_checker = get_win_checker()
        self.state = GameState.WAITING
        self.players: List[Player] = []
        self.player_symbols: Dict[str, str] = {}  # player_id -> symbol
        self.current_player_index = 0
        self.move_history: List[Tuple[str, int, int, int, int]] = []  # (player_id, w, x, y, z)
        self.winner: Optional[Player] = None
        self.winning_line: Optional[List[Tuple[int, int, int, int]]] = None
    
    def add_player(self, player_id: str, player_name: str, symbol: str, is_bot: bool = False) -> bool:
        """
        Add a player to the game.
        
        Args:
            player_id: Unique player identifier
            player_name: Display name
            symbol: Player symbol (1-2 characters, must be unique)
            is_bot: Whether this is an AI bot
            
        Returns:
            True if player was added, False otherwise
        """
        if self.state != GameState.WAITING:
            return False
        
        if len(self.players) >= self.MAX_PLAYERS:
            return False
        
        # Check if symbol is already taken
        if symbol in [p.symbol for p in self.players]:
            return False
        
        # Validate symbol (1-2 characters)
        if not symbol or len(symbol) > 2:
            return False
        
        player = Player(player_id, player_name, symbol, is_bot)
        self.players.append(player)
        self.player_symbols[player_id] = symbol
        
        return True
    
    def start_game(self) -> bool:
        """
        Start the game.
        
        Returns:
            True if game was started, False otherwise
        """
        if self.state != GameState.WAITING:
            return False
        
        if len(self.players) < self.MIN_PLAYERS:
            return False
        
        self.state = GameState.PLAYING
        self.current_player_index = 0
        self.board = Board()  # Reset board
        self.move_history = []
        self.winner = None
        self.winning_line = None
        
        return True
    
    def get_current_player(self) -> Optional[Player]:
        """Get the current player whose turn it is."""
        if self.state != GameState.PLAYING:
            return None
        
        if not self.players:
            return None
        
        return self.players[self.current_player_index]
    
    def make_move(self, player_id: str, w: int, x: int, y: int, z: int) -> Tuple[bool, Optional[str]]:
        """
        Make a move.
        
        Args:
            player_id: ID of the player making the move
            w, x, y, z: Coordinates (0-2 each)
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.state != GameState.PLAYING:
            return False, "Game is not in playing state"
        
        current_player = self.get_current_player()
        if current_player is None or current_player.player_id != player_id:
            return False, "Not your turn"
        
        if not self.board.is_valid_move(w, x, y, z):
            return False, "Invalid move position"
        
        # Make the move
        player_symbol = self.player_symbols[player_id]
        if not self.board.make_move(player_symbol, w, x, y, z):
            return False, "Failed to make move"
        
        # Record move
        self.move_history.append((player_id, w, x, y, z))
        
        # Check for win
        winner_symbol = self.win_checker.check_win(self.board, w, x, y, z)
        if winner_symbol:
            # Find the winning player
            for player in self.players:
                if player.symbol == winner_symbol:
                    self.winner = player
                    self.winning_line = self.win_checker.get_winning_line(self.board, winner_symbol)
                    break
            self.state = GameState.FINISHED
            return True, None
        
        # Check for draw (board full)
        if len(self.board.get_empty_positions()) == 0:
            self.state = GameState.FINISHED
            return True, None
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        return True, None
    
    def check_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state == GameState.FINISHED
    
    def get_game_status(self) -> Dict:
        """
        Get current game status.
        
        Returns:
            Dictionary with game status information
        """
        return {
            'state': self.state.value,
            'current_player': self.get_current_player().player_id if self.get_current_player() else None,
            'players': [{'id': p.player_id, 'name': p.player_name, 'symbol': p.symbol, 'is_bot': p.is_bot} 
                       for p in self.players],
            'move_count': len(self.move_history),
            'winner': self.winner.player_id if self.winner else None,
            'board_full': len(self.board.get_empty_positions()) == 0
        }
    
    def get_board_copy(self) -> Board:
        """Get a copy of the current board."""
        return self.board.copy()

