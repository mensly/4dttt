"""
Template for future trainable AI (neural network/reinforcement learning).
This is a placeholder for Phase 1 that can be extended later.
"""

from typing import Tuple
from ..core.board import Board
from .base_ai import BaseAI
from .simple_ai import SimpleAI


class TrainableAI(BaseAI):
    """
    Template for trainable AI using machine learning.
    Currently falls back to SimpleAI behavior but provides interface for training.
    """
    
    def __init__(self, player_symbol: str, player_name: str = "TrainableAI"):
        """Initialize the trainable AI."""
        super().__init__(player_symbol, player_name)
        self.fallback_ai = SimpleAI(player_symbol, player_name)
        self.training_data = []  # Store game states for training
    
    def get_move(self, board: Board) -> Tuple[int, int, int, int]:
        """
        Get the next move.
        
        Currently uses fallback AI, but can be extended to use trained model.
        
        Args:
            board: Current game board
            
        Returns:
            Tuple of (w, x, y, z) coordinates for the move
        """
        # For now, use simple AI as fallback
        # TODO: Implement neural network inference here
        return self.fallback_ai.get_move(board)
    
    def record_game_state(self, board: Board, move: Tuple[int, int, int, int], reward: float = None):
        """
        Record a game state for training.
        
        Args:
            board: Game board state
            move: Move made
            reward: Optional reward signal
        """
        # TODO: Implement training data collection
        self.training_data.append({
            'board': board.get_board_state(),
            'move': move,
            'reward': reward
        })
    
    def train(self, training_data: list = None):
        """
        Train the AI model.
        
        Args:
            training_data: Optional training data (uses self.training_data if None)
        """
        # TODO: Implement training logic (neural network, reinforcement learning, etc.)
        pass

