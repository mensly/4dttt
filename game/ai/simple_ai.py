"""
Simple heuristic-based AI for 4D Tic-Tac-Toe.
Uses basic strategy: win > block > center > random
"""

import random
from typing import Tuple, List, Optional
from ..core.board import Board
from ..core.win_checker import get_win_checker
from .base_ai import BaseAI


class SimpleAI(BaseAI):
    """Simple heuristic-based AI that uses basic strategies."""
    
    def __init__(self, player_symbol: str, player_name: str = "SimpleAI"):
        """Initialize the simple AI."""
        super().__init__(player_symbol, player_name)
        self.win_checker = get_win_checker()
    
    def get_move(self, board: Board) -> Tuple[int, int, int, int]:
        """
        Get the next move using simple heuristics.
        Strategy: win immediately > block opponent > take center > random valid move
        
        Args:
            board: Current game board
            
        Returns:
            Tuple of (w, x, y, z) coordinates for the move
        """
        empty_positions = board.get_empty_positions()
        
        if not empty_positions:
            raise ValueError("No valid moves available")
        
        # Strategy 1: Check for immediate win
        winning_move = self._find_winning_move(board)
        if winning_move:
            return winning_move
        
        # Strategy 2: Block opponent from winning
        blocking_move = self._find_blocking_move(board)
        if blocking_move:
            return blocking_move
        
        # Strategy 3: Prefer center positions
        center_positions = [(1, 1, 1, 1), (1, 1, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1),
                           (1, 1, 1, 2), (1, 1, 2, 1), (1, 2, 1, 1), (2, 1, 1, 1),
                           (1, 1, 0, 0), (1, 0, 1, 0), (0, 1, 1, 0), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]
        available_centers = [pos for pos in center_positions if pos in empty_positions]
        if available_centers:
            return random.choice(available_centers)
        
        # Strategy 4: Random valid move
        return random.choice(empty_positions)
    
    def _find_winning_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """
        Find a move that would result in an immediate win.
        
        Args:
            board: Current game board
            
        Returns:
            Winning move coordinates or None
        """
        empty_positions = board.get_empty_positions()
        
        for w, x, y, z in empty_positions:
            # Try making this move
            test_board = board.copy()
            test_board.make_move(self.player_symbol, w, x, y, z)
            
            # Check if this move wins
            winner = self.win_checker.check_win(test_board, w, x, y, z)
            if winner == self.player_symbol:
                return (w, x, y, z)
        
        return None
    
    def _find_blocking_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """
        Find a move that blocks an opponent from winning.
        
        Args:
            board: Current game board
            
        Returns:
            Blocking move coordinates or None
        """
        empty_positions = board.get_empty_positions()
        
        # Get all player symbols on the board
        all_symbols = set()
        for w, x, y, z in board.get_all_positions():
            symbol = board.get(w, x, y, z)
            if symbol and symbol != self.player_symbol:
                all_symbols.add(symbol)
        
        # For each opponent symbol, check if they can win
        for opponent_symbol in all_symbols:
            for w, x, y, z in empty_positions:
                # Try opponent making this move
                test_board = board.copy()
                test_board.make_move(opponent_symbol, w, x, y, z)
                
                # Check if opponent would win
                winner = self.win_checker.check_win(test_board, w, x, y, z)
                if winner == opponent_symbol:
                    # Block this move
                    return (w, x, y, z)
        
        return None

