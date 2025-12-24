"""
Data-driven AI that learns from training data.
Uses statistical analysis of winning/losing moves to improve decision-making.
"""

import json
import gzip
import random
from typing import Tuple, List, Optional, Dict
from pathlib import Path
from collections import defaultdict, Counter
from ..core.board import Board
from ..core.win_checker import get_win_checker
from .base_ai import BaseAI
from .simple_ai import SimpleAI


class LearnedAI(BaseAI):
    """
    AI that learns from training data to make better moves.
    Uses statistical analysis of move patterns from training games.
    """
    
    def __init__(self, player_symbol: str, player_name: str = "LearnedAI", training_data_path: str = None):
        """
        Initialize the learned AI.
        
        Args:
            player_symbol: Symbol this AI plays as
            player_name: Name of this AI player
            training_data_path: Path to training_data.json file
        """
        super().__init__(player_symbol, player_name)
        self.win_checker = get_win_checker()
        self.fallback_ai = SimpleAI(player_symbol, player_name)
        
        # Move statistics from training data
        self.move_scores: Dict[Tuple[int, int, int, int], float] = {}
        self.winning_moves: List[Tuple[int, int, int, int]] = []
        self.losing_moves: List[Tuple[int, int, int, int]] = []
        self.position_frequencies: Dict[Tuple[int, int, int, int], int] = defaultdict(int)
        
        # Load training data if available
        if training_data_path:
            self.load_training_data(training_data_path)
        else:
            # Try to find training_data.json or training_data.json.gz in common locations
            default_paths = [
                Path('training_data.json.gz'),
                Path('training_data.json'),
                Path('../training_data.json.gz'),
                Path('../training_data.json'),
                Path('../../training_data.json.gz'),
                Path('../../training_data.json'),
            ]
            for path in default_paths:
                if path.exists():
                    self.load_training_data(str(path))
                    break
    
    def load_training_data(self, file_path: str):
        """
        Load and analyze training data from JSON file (supports gzipped files).
        
        Args:
            file_path: Path to training_data.json or training_data.json.gz
        """
        try:
            # Check if file is gzipped
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    training_data = json.load(f)
            else:
                with open(file_path, 'r') as f:
                    training_data = json.load(f)
            
            print(f"Loaded training data from {file_path}")
            print(f"  Games: {len(training_data)}")
            
            # Analyze moves
            winning_move_positions = []
            losing_move_positions = []
            all_move_positions = []
            
            for game_data in training_data:
                winner_id = game_data.get('winner')
                is_draw = game_data.get('is_draw', False)
                
                for move_data in game_data.get('moves', []):
                    move = tuple(move_data['move'])
                    all_move_positions.append(move)
                    self.position_frequencies[move] += 1
                    
                    reward = move_data.get('reward', 0)
                    player_id = move_data.get('player_id')
                    
                    if reward > 0:  # Winning move
                        winning_move_positions.append(move)
                    elif reward < 0:  # Losing move
                        losing_move_positions.append(move)
            
            # Calculate move scores
            # Score = (wins - losses) / total_occurrences
            move_counts = Counter(all_move_positions)
            win_counts = Counter(winning_move_positions)
            loss_counts = Counter(losing_move_positions)
            
            for move in move_counts:
                wins = win_counts.get(move, 0)
                losses = loss_counts.get(move, 0)
                total = move_counts[move]
                
                # Score ranges from -1 (always loses) to +1 (always wins)
                if total > 0:
                    score = (wins - losses) / total
                    self.move_scores[move] = score
            
            self.winning_moves = winning_move_positions
            self.losing_moves = losing_move_positions
            
            print(f"  Total moves analyzed: {len(all_move_positions)}")
            print(f"  Unique positions: {len(move_counts)}")
            print(f"  Winning moves: {len(winning_move_positions)}")
            print(f"  Losing moves: {len(losing_move_positions)}")
            print(f"  Move scores calculated: {len(self.move_scores)}")
            
        except FileNotFoundError:
            print(f"Warning: Training data file not found: {file_path}")
            print("  Falling back to SimpleAI behavior")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in training data: {e}")
            print("  Falling back to SimpleAI behavior")
        except Exception as e:
            print(f"Error loading training data: {e}")
            print("  Falling back to SimpleAI behavior")
    
    def get_move(self, board: Board) -> Tuple[int, int, int, int]:
        """
        Get the next move using learned patterns from training data.
        Strategy: win > block > learned good moves > center > random
        
        Args:
            board: Current game board
            
        Returns:
            Tuple of (w, x, y, z) coordinates for the move
        """
        empty_positions = board.get_empty_positions()
        
        if not empty_positions:
            raise ValueError("No valid moves available")
        
        # Strategy 1: Check for immediate win (always prioritize)
        winning_move = self._find_winning_move(board)
        if winning_move:
            return winning_move
        
        # Strategy 2: Block opponent from winning (always prioritize)
        blocking_move = self._find_blocking_move(board)
        if blocking_move:
            return blocking_move
        
        # Strategy 3: Use learned move scores to prefer good positions
        if self.move_scores:
            scored_moves = []
            for pos in empty_positions:
                score = self.move_scores.get(pos, 0.0)
                scored_moves.append((pos, score))
            
            # Sort by score (highest first)
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            
            # Filter moves with positive scores (or top 20% if all negative)
            good_moves = [pos for pos, score in scored_moves if score > 0]
            if good_moves:
                # Prefer moves with highest scores, but add some randomness
                top_moves = [pos for pos, score in scored_moves[:max(1, len(scored_moves) // 5)] if score >= scored_moves[0][1] - 0.1]
                return random.choice(top_moves)
            
            # If no good moves, avoid worst moves
            worst_moves = [pos for pos, score in scored_moves if score < -0.3]
            if worst_moves and len(empty_positions) > len(worst_moves):
                available = [pos for pos in empty_positions if pos not in worst_moves]
                if available:
                    # Use learned scores among remaining moves
                    remaining_scored = [(pos, self.move_scores.get(pos, 0.0)) for pos in available]
                    remaining_scored.sort(key=lambda x: x[1], reverse=True)
                    top_remaining = remaining_scored[:max(1, len(remaining_scored) // 3)]
                    return random.choice([pos for pos, _ in top_remaining])
        
        # Strategy 4: Prefer center positions (fallback)
        center_positions = [(1, 1, 1, 1), (1, 1, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1),
                           (1, 1, 1, 2), (1, 1, 2, 1), (1, 2, 1, 1), (2, 1, 1, 1),
                           (1, 1, 0, 0), (1, 0, 1, 0), (0, 1, 1, 0), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]
        available_centers = [pos for pos in center_positions if pos in empty_positions]
        if available_centers:
            return random.choice(available_centers)
        
        # Strategy 5: Random valid move (last resort)
        return random.choice(empty_positions)
    
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
    
    def _find_blocking_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """Find a move that blocks an opponent from winning."""
        empty_positions = board.get_empty_positions()
        
        all_symbols = set()
        for w, x, y, z in board.get_all_positions():
            symbol = board.get(w, x, y, z)
            if symbol and symbol != self.player_symbol:
                all_symbols.add(symbol)
        
        for opponent_symbol in all_symbols:
            for w, x, y, z in empty_positions:
                test_board = board.copy()
                test_board.make_move(opponent_symbol, w, x, y, z)
                
                winner = self.win_checker.check_win(test_board, w, x, y, z)
                if winner == opponent_symbol:
                    return (w, x, y, z)
        
        return None
    
    def get_move_statistics(self) -> Dict:
        """Get statistics about learned moves."""
        return {
            'total_learned_moves': len(self.move_scores),
            'winning_moves_count': len(self.winning_moves),
            'losing_moves_count': len(self.losing_moves),
            'top_moves': sorted(self.move_scores.items(), key=lambda x: x[1], reverse=True)[:10],
            'worst_moves': sorted(self.move_scores.items(), key=lambda x: x[1])[:10]
        }

