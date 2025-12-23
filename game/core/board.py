"""
4D Board representation for Tic-Tac-Toe.
Represents a 3×3×3×3 hypercube (81 positions total).
"""

from typing import Optional, List, Tuple


class Board:
    """Represents a 4D Tic-Tac-Toe board (3×3×3×3)."""
    
    SIZE = 3
    TOTAL_POSITIONS = SIZE ** 4  # 81
    
    def __init__(self):
        """Initialize an empty 4D board."""
        # Use a 4D nested list structure: board[w][x][y][z]
        # Each dimension has indices 0-2
        self.board = [[[[None for _ in range(self.SIZE)] 
                       for _ in range(self.SIZE)]
                       for _ in range(self.SIZE)]
                       for _ in range(self.SIZE)]
        
    def get(self, w: int, x: int, y: int, z: int) -> Optional[str]:
        """
        Get the value at position (w, x, y, z).
        
        Args:
            w, x, y, z: Coordinates (0-2 each)
            
        Returns:
            Player symbol (string) or None if empty
        """
        if not self.is_valid_position(w, x, y, z):
            raise ValueError(f"Invalid position: ({w}, {x}, {y}, {z})")
        return self.board[w][x][y][z]
    
    def set(self, w: int, x: int, y: int, z: int, value: Optional[str]) -> None:
        """
        Set the value at position (w, x, y, z).
        
        Args:
            w, x, y, z: Coordinates (0-2 each)
            value: Player symbol (string) or None
        """
        if not self.is_valid_position(w, x, y, z):
            raise ValueError(f"Invalid position: ({w}, {x}, {y}, {z})")
        self.board[w][x][y][z] = value
    
    def is_valid_position(self, w: int, x: int, y: int, z: int) -> bool:
        """Check if coordinates are valid (all in range 0-2)."""
        return (0 <= w < self.SIZE and 0 <= x < self.SIZE and
                0 <= y < self.SIZE and 0 <= z < self.SIZE)
    
    def is_valid_move(self, w: int, x: int, y: int, z: int) -> bool:
        """
        Check if a move is valid (position is valid and empty).
        
        Args:
            w, x, y, z: Coordinates (0-2 each)
            
        Returns:
            True if move is valid, False otherwise
        """
        if not self.is_valid_position(w, x, y, z):
            return False
        return self.board[w][x][y][z] is None
    
    def make_move(self, player_symbol: str, w: int, x: int, y: int, z: int) -> bool:
        """
        Make a move at the specified position.
        
        Args:
            player_symbol: Symbol of the player making the move
            w, x, y, z: Coordinates (0-2 each)
            
        Returns:
            True if move was made successfully, False otherwise
        """
        if not self.is_valid_move(w, x, y, z):
            return False
        self.board[w][x][y][z] = player_symbol
        return True
    
    def get_board_state(self) -> List[List[List[List[Optional[str]]]]]:
        """
        Get a copy of the current board state.
        
        Returns:
            4D nested list representing the board
        """
        # Deep copy the board
        return [[[[self.board[w][x][y][z] 
                  for z in range(self.SIZE)]
                  for y in range(self.SIZE)]
                  for x in range(self.SIZE)]
                  for w in range(self.SIZE)]
    
    def get_all_positions(self) -> List[Tuple[int, int, int, int]]:
        """
        Get all 81 positions as tuples.
        
        Returns:
            List of (w, x, y, z) tuples
        """
        positions = []
        for w in range(self.SIZE):
            for x in range(self.SIZE):
                for y in range(self.SIZE):
                    for z in range(self.SIZE):
                        positions.append((w, x, y, z))
        return positions
    
    def get_empty_positions(self) -> List[Tuple[int, int, int, int]]:
        """
        Get all empty positions.
        
        Returns:
            List of (w, x, y, z) tuples for empty positions
        """
        empty = []
        for w, x, y, z in self.get_all_positions():
            if self.board[w][x][y][z] is None:
                empty.append((w, x, y, z))
        return empty
    
    def count_moves(self) -> int:
        """Count the number of moves made on the board."""
        return self.TOTAL_POSITIONS - len(self.get_empty_positions())
    
    def copy(self) -> 'Board':
        """Create a deep copy of this board."""
        new_board = Board()
        for w in range(self.SIZE):
            for x in range(self.SIZE):
                for y in range(self.SIZE):
                    for z in range(self.SIZE):
                        new_board.board[w][x][y][z] = self.board[w][x][y][z]
        return new_board
    
    def __str__(self) -> str:
        """String representation for debugging."""
        lines = []
        for w in range(self.SIZE):
            for y in range(self.SIZE):
                row = []
                for x in range(self.SIZE):
                    cells = []
                    for z in range(self.SIZE):
                        cell = self.board[w][x][y][z]
                        cells.append(cell if cell else '.')
                    row.append(' '.join(cells))
                lines.append(f"W{w}Y{y}: {' | '.join(row)}")
        return '\n'.join(lines)

