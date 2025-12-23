"""
Minimax AI with alpha-beta pruning for 4D Tic-Tac-Toe.
Uses depth-limited search due to large state space.
"""

import math
from typing import Tuple, Optional, List
from ..core.board import Board
from ..core.win_checker import get_win_checker
from .base_ai import BaseAI


class MinimaxAI(BaseAI):
    """
    Minimax AI with alpha-beta pruning.
    Uses depth-limited search (default depth 2-3) due to large state space.
    """
    
    def __init__(self, player_symbol: str, player_name: str = "MinimaxAI", max_depth: int = 2):
        """
        Initialize the minimax AI.
        
        Args:
            player_symbol: Symbol this AI plays as
            player_name: Name of this AI player
            max_depth: Maximum search depth (lower for faster play)
        """
        super().__init__(player_symbol, player_name)
        self.win_checker = get_win_checker()
        self.max_depth = max_depth
    
    def get_move(self, board: Board, opponent_symbols: List[str] = None) -> Tuple[int, int, int, int]:
        """
        Get the next move using minimax algorithm.
        
        Args:
            board: Current game board
            opponent_symbols: List of opponent symbols (if None, detects from board)
            
        Returns:
            Tuple of (w, x, y, z) coordinates for the move
        """
        if opponent_symbols is None:
            opponent_symbols = self._get_opponent_symbols(board)
        
        empty_positions = board.get_empty_positions()
        
        if not empty_positions:
            raise ValueError("No valid moves available")
        
        # Check for immediate win (fast path)
        winning_move = self._find_winning_move(board)
        if winning_move:
            return winning_move
        
        # Check for blocking move (fast path)
        blocking_move = self._find_blocking_move(board, opponent_symbols)
        if blocking_move:
            return blocking_move
        
        # Use minimax for remaining moves
        best_move = None
        best_score = -math.inf
        
        for w, x, y, z in empty_positions:
            test_board = board.copy()
            test_board.make_move(self.player_symbol, w, x, y, z)
            
            # Check if this move wins immediately
            winner = self.win_checker.check_win(test_board, w, x, y, z)
            if winner == self.player_symbol:
                return (w, x, y, z)
            
            # Evaluate this position
            score = self._minimax(test_board, self.max_depth - 1, False, 
                                 opponent_symbols, -math.inf, math.inf)
            
            if score > best_score:
                best_score = score
                best_move = (w, x, y, z)
        
        return best_move if best_move else empty_positions[0]
    
    def _minimax(self, board: Board, depth: int, maximizing: bool, 
                 opponent_symbols: List[str], alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            maximizing: True if maximizing player's turn
            opponent_symbols: List of opponent symbols
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            
        Returns:
            Evaluation score
        """
        # Terminal states
        if depth == 0:
            return self._evaluate_position(board)
        
        empty_positions = board.get_empty_positions()
        
        # Check for win/draw
        # Note: We check all positions here since we don't know last move
        winner = self.win_checker.check_win_all_positions(board)
        if winner:
            if winner == self.player_symbol:
                return 1000  # Win
            else:
                return -1000  # Loss
        
        if not empty_positions:
            return 0  # Draw
        
        if maximizing:
            max_eval = -math.inf
            for w, x, y, z in empty_positions:
                test_board = board.copy()
                test_board.make_move(self.player_symbol, w, x, y, z)
                
                # Check immediate win
                move_winner = self.win_checker.check_win(test_board, w, x, y, z)
                if move_winner == self.player_symbol:
                    return 1000
                
                eval_score = self._minimax(test_board, depth - 1, False, 
                                          opponent_symbols, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return max_eval
        else:
            min_eval = math.inf
            for w, x, y, z in empty_positions:
                # Try moves for all opponents
                for opponent_symbol in opponent_symbols:
                    test_board = board.copy()
                    test_board.make_move(opponent_symbol, w, x, y, z)
                    
                    # Check immediate loss
                    move_winner = self.win_checker.check_win(test_board, w, x, y, z)
                    if move_winner == opponent_symbol:
                        return -1000
                    
                    eval_score = self._minimax(test_board, depth - 1, True, 
                                              opponent_symbols, alpha, beta)
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            return min_eval
    
    def _evaluate_position(self, board: Board) -> float:
        """
        Evaluate a board position heuristically.
        
        Args:
            board: Board to evaluate
            
        Returns:
            Evaluation score (positive is good for this AI)
        """
        score = 0.0
        
        # Count potential winning lines
        winning_lines = self.win_checker.get_all_winning_lines()
        
        for line in winning_lines:
            symbols = []
            for w, x, y, z in line:
                symbols.append(board.get(w, x, y, z))
            
            my_count = symbols.count(self.player_symbol)
            opponent_count = sum(1 for s in symbols if s and s != self.player_symbol)
            empty_count = symbols.count(None)
            
            # Favor lines where we have more pieces and opponents have fewer
            if my_count > 0 and opponent_count == 0:
                score += my_count * 10  # Potential winning line
            elif opponent_count > 0 and my_count == 0:
                score -= opponent_count * 10  # Opponent's potential winning line
        
        return score
    
    def _get_opponent_symbols(self, board: Board) -> List[str]:
        """Get all opponent symbols from the board."""
        symbols = set()
        for w, x, y, z in board.get_all_positions():
            symbol = board.get(w, x, y, z)
            if symbol and symbol != self.player_symbol:
                symbols.add(symbol)
        return list(symbols)
    
    def _find_winning_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """Find a move that would result in an immediate win."""
        empty_positions = board.get_empty_positions()
        
        for w, x, y, z in empty_positions:
            test_board = board.copy()
            test_board.make_move(self.player_symbol, w, x, y, z)
            
            winner = self.win_checker.check_win(test_board, w, x, y, z)
            if winner == self.player_symbol:
                return (w, x, y, z)
        
        return None
    
    def _find_blocking_move(self, board: Board, opponent_symbols: List[str]) -> Optional[Tuple[int, int, int, int]]:
        """Find a move that blocks an opponent from winning."""
        empty_positions = board.get_empty_positions()
        
        for opponent_symbol in opponent_symbols:
            for w, x, y, z in empty_positions:
                test_board = board.copy()
                test_board.make_move(opponent_symbol, w, x, y, z)
                
                winner = self.win_checker.check_win(test_board, w, x, y, z)
                if winner == opponent_symbol:
                    return (w, x, y, z)
        
        return None

