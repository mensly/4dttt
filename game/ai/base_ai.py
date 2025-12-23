"""
Base AI interface for 4D Tic-Tac-Toe bots.
"""

from abc import ABC, abstractmethod
from typing import Tuple
from ..core.board import Board


class BaseAI(ABC):
    """Base class for AI implementations."""
    
    def __init__(self, player_symbol: str, player_name: str = None):
        """
        Initialize the AI.
        
        Args:
            player_symbol: Symbol this AI plays as
            player_name: Name of this AI player
        """
        self.player_symbol = player_symbol
        self.player_name = player_name or f"AI-{player_symbol}"
    
    @abstractmethod
    def get_move(self, board: Board) -> Tuple[int, int, int, int]:
        """
        Get the next move for this AI.
        
        Args:
            board: Current game board
            
        Returns:
            Tuple of (w, x, y, z) coordinates for the move
        """
        pass
    
    def get_name(self) -> str:
        """Get the AI's name."""
        return self.player_name
    
    def get_symbol(self) -> str:
        """Get the AI's symbol."""
        return self.player_symbol

