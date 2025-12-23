"""
Efficient win checker for 4D Tic-Tac-Toe.
Checks all possible 3-point paths in a 3×3×3×3 hypercube.
"""

from typing import Optional, List, Tuple, Set
from .board import Board


class WinChecker:
    """
    Efficient win detection for 4D Tic-Tac-Toe.
    Pre-computes all possible winning lines at initialization.
    """
    
    # All possible direction vectors in 4D space
    # Each direction can be (0,0,0,0) to (1,1,1,1) in each component
    # We generate all 3^4 - 1 = 80 directions (excluding (0,0,0,0))
    DIRECTIONS = []
    
    def __init__(self):
        """Initialize win checker and pre-compute all winning lines."""
        self._generate_directions()
        self._winning_lines = self._precompute_winning_lines()
        # Create a map: position -> list of winning lines passing through it
        self._position_to_lines = self._build_position_line_map()
    
    def _generate_directions(self) -> None:
        """Generate all valid direction vectors for 4D space."""
        directions = []
        # Generate all combinations of -1, 0, 1 for each dimension
        # Exclude (0,0,0,0) as it's not a valid direction
        for dw in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if (dw, dx, dy, dz) != (0, 0, 0, 0):
                            directions.append((dw, dx, dy, dz))
        WinChecker.DIRECTIONS = directions
    
    def _precompute_winning_lines(self) -> List[List[Tuple[int, int, int, int]]]:
        """
        Pre-compute all possible winning lines (3 positions in a row).
        
        A winning line consists of 3 positions that form a straight line.
        We iterate through all possible starting positions and directions.
        
        Returns:
            List of winning lines, each line is a list of 3 (w,x,y,z) tuples
        """
        lines = []
        lines_set = set()  # To avoid duplicates
        
        # For each starting position
        for w in range(3):
            for x in range(3):
                for y in range(3):
                    for z in range(3):
                        # For each direction
                        for dw, dx, dy, dz in WinChecker.DIRECTIONS:
                            # Check if we can extend 2 steps in this direction
                            positions = []
                            valid = True
                            
                            for step in range(3):
                                nw = w + step * dw
                                nx = x + step * dx
                                ny = y + step * dy
                                nz = z + step * dz
                                
                                # Check if position is valid
                                if not (0 <= nw < 3 and 0 <= nx < 3 and 
                                       0 <= ny < 3 and 0 <= nz < 3):
                                    valid = False
                                    break
                                
                                positions.append((nw, nx, ny, nz))
                            
                            if valid:
                                # Create a canonical representation (sorted tuple)
                                line_tuple = tuple(sorted(positions))
                                if line_tuple not in lines_set:
                                    lines_set.add(line_tuple)
                                    lines.append(positions)
        
        return lines
    
    def _build_position_line_map(self) -> dict:
        """
        Build a map from position to list of winning lines passing through it.
        
        Returns:
            Dictionary mapping (w,x,y,z) -> list of line indices
        """
        position_map = {}
        
        for line_idx, line in enumerate(self._winning_lines):
            for pos in line:
                if pos not in position_map:
                    position_map[pos] = []
                position_map[pos].append(line_idx)
        
        return position_map
    
    def get_all_winning_lines(self) -> List[List[Tuple[int, int, int, int]]]:
        """
        Get all pre-computed winning lines.
        
        Returns:
            List of winning lines
        """
        return self._winning_lines
    
    def check_win(self, board: Board, last_move_w: int, last_move_x: int, 
                  last_move_y: int, last_move_z: int) -> Optional[str]:
        """
        Check if the last move resulted in a win.
        
        This is optimized to only check lines passing through the last move position.
        
        Args:
            board: The game board
            last_move_w, last_move_x, last_move_y, last_move_z: Last move position
            
        Returns:
            Player symbol if there's a winner, None otherwise
        """
        last_pos = (last_move_w, last_move_x, last_move_y, last_move_z)
        player_symbol = board.get(last_move_w, last_move_x, last_move_y, last_move_z)
        
        if player_symbol is None:
            return None
        
        # Only check lines passing through the last move position
        if last_pos not in self._position_to_lines:
            return None
        
        line_indices = self._position_to_lines[last_pos]
        
        for line_idx in line_indices:
            line = self._winning_lines[line_idx]
            # Check if all 3 positions in this line have the same symbol
            symbols = []
            for w, x, y, z in line:
                symbol = board.get(w, x, y, z)
                symbols.append(symbol)
            
            # Check if all are the same and not None
            if symbols[0] is not None and all(s == symbols[0] for s in symbols):
                return symbols[0]
        
        return None
    
    def check_win_all_positions(self, board: Board) -> Optional[str]:
        """
        Check for a win by examining all positions (less efficient but thorough).
        
        This is a fallback method that checks all winning lines.
        
        Args:
            board: The game board
            
        Returns:
            Player symbol if there's a winner, None otherwise
        """
        for line in self._winning_lines:
            symbols = []
            for w, x, y, z in line:
                symbol = board.get(w, x, y, z)
                symbols.append(symbol)
            
            # Check if all are the same and not None
            if symbols[0] is not None and all(s == symbols[0] for s in symbols):
                return symbols[0]
        
        return None
    
    def get_winning_line(self, board: Board, player_symbol: str) -> Optional[List[Tuple[int, int, int, int]]]:
        """
        Get the winning line for a player (if they won).
        
        Args:
            board: The game board
            player_symbol: Symbol of the player to check
            
        Returns:
            Winning line as list of positions, or None if no win
        """
        for line in self._winning_lines:
            symbols = []
            for w, x, y, z in line:
                symbol = board.get(w, x, y, z)
                symbols.append(symbol)
            
            if all(s == player_symbol for s in symbols):
                return line
        
        return None
    
    def count_winning_lines(self) -> int:
        """Get the total number of winning lines."""
        return len(self._winning_lines)


# Create a global instance for convenience
_global_win_checker = None

def get_win_checker() -> WinChecker:
    """Get the global win checker instance (singleton pattern)."""
    global _global_win_checker
    if _global_win_checker is None:
        _global_win_checker = WinChecker()
    return _global_win_checker

