"""
Grid display for 4D Tic-Tac-Toe board.
Renders as a 9×9 grid representing 3×3 grid of 3×3 mini-boards.
"""

from typing import Optional
from ..core.board import Board


class GridDisplay:
    """
    Displays a 4D board as a 9×9 grid.
    
    Mapping: 4D coordinates (w,x,y,z) -> 2D grid (row, col)
    grid_row = w * 3 + y
    grid_col = x * 3 + z
    """
    
    def __init__(self):
        """Initialize the grid display."""
        pass
    
    def render_board(self, board: Board, highlight_last_move: Optional[tuple] = None,
                    highlight_winning_line: Optional[list] = None) -> str:
        """
        Render the board as a 9×9 grid string.
        
        Args:
            board: The game board to render
            highlight_last_move: Optional (w, x, y, z) tuple to highlight
            highlight_winning_line: Optional list of (w, x, y, z) tuples to highlight
            
        Returns:
            Formatted string representation of the board
        """
        # Create 9×9 grid
        grid = [[' ' for _ in range(9)] for _ in range(9)]
        highlights = set()
        
        if highlight_last_move:
            w, x, y, z = highlight_last_move
            row, col = self.coord_to_grid(w, x, y, z)
            highlights.add((row, col))
        
        if highlight_winning_line:
            for pos in highlight_winning_line:
                w, x, y, z = pos
                row, col = self.coord_to_grid(w, x, y, z)
                highlights.add((row, col))
        
        # Fill grid from board
        for w in range(3):
            for x in range(3):
                for y in range(3):
                    for z in range(3):
                        row, col = self.coord_to_grid(w, x, y, z)
                        cell_value = board.get(w, x, y, z)
                        grid[row][col] = self.format_cell(cell_value)
        
        # Build output string
        lines = []
        # Calculate width: row prefix "X |" (3 chars) + 9 columns * " X |" (5 chars each) = 48
        row_width = 3 + 9 * 5  # "X |" + 9 * " X |"
        lines.append("=" * row_width)
        # Header: account for row number space, then align column numbers
        # Each column number should be centered in its " X |" space (5 chars)
        header = "   "  # Space for row number prefix
        for col in range(9):
            header += f"  {col} |"  # "  N |" format to center number
        lines.append(header)
        lines.append("=" * row_width)
        
        for row in range(9):
            row_str = f"{row} |"
            for col in range(9):
                cell = grid[row][col]
                if (row, col) in highlights:
                    # Highlight with brackets
                    row_str += f"[{cell}]|"
                else:
                    row_str += f" {cell} |"
            lines.append(row_str)
            if (row + 1) % 3 == 0 and row < 8:
                lines.append("-" * row_width)
        
        lines.append("=" * row_width)
        lines.append("\nMini-board regions:")
        lines.append("  W0: rows 0-2,  W1: rows 3-5,  W2: rows 6-8")
        lines.append("  X0: cols 0-2,  X1: cols 3-5,  X2: cols 6-8")
        
        return "\n".join(lines)
    
    def coord_to_grid(self, w: int, x: int, y: int, z: int) -> tuple:
        """
        Convert 4D coordinates to 2D grid position.
        
        Args:
            w, x, y, z: 4D coordinates (0-2 each)
            
        Returns:
            (row, col) tuple for the 9×9 grid
        """
        grid_row = w * 3 + y
        grid_col = x * 3 + z
        return (grid_row, grid_col)
    
    def grid_to_coord(self, row: int, col: int) -> tuple:
        """
        Convert 2D grid position to 4D coordinates.
        
        Args:
            row, col: Grid coordinates (0-8 each)
            
        Returns:
            (w, x, y, z) tuple for 4D coordinates
        """
        w = row // 3
        y = row % 3
        x = col // 3
        z = col % 3
        return (w, x, y, z)
    
    def format_cell(self, cell_value: Optional[str]) -> str:
        """
        Format a cell value for display.
        
        Args:
            cell_value: Player symbol or None
            
        Returns:
            Formatted string (2 characters wide)
        """
        if cell_value is None:
            return " ."
        # Pad to 2 characters for alignment
        return cell_value.ljust(2)[:2]
    
    def get_mini_board_bounds(self, mini_w: int, mini_x: int) -> dict:
        """
        Get the grid bounds for a mini-board.
        
        Args:
            mini_w, mini_x: Mini-board coordinates (0-2 each)
            
        Returns:
            Dictionary with 'row_start', 'row_end', 'col_start', 'col_end'
        """
        row_start = mini_w * 3
        row_end = row_start + 3
        col_start = mini_x * 3
        col_end = col_start + 3
        
        return {
            'row_start': row_start,
            'row_end': row_end,
            'col_start': col_start,
            'col_end': col_end
        }

