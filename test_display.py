"""
Test the display functionality.
"""

from game.core.board import Board
from game.display.grid_display import GridDisplay


def test_display():
    """Test grid display."""
    print("Testing Grid Display")
    print("=" * 60 + "\n")
    
    board = Board()
    display = GridDisplay()
    
    # Make some moves in different regions
    board.make_move('X', 0, 0, 0, 0)  # Top-left mini-board
    board.make_move('O', 1, 1, 1, 1)  # Center
    board.make_move('A', 2, 2, 2, 2)  # Bottom-right mini-board
    board.make_move('B', 0, 2, 1, 0)  # Top-right mini-board
    
    print("Board with moves at:")
    print("  X at (0,0,0,0) - top-left")
    print("  O at (1,1,1,1) - center")
    print("  A at (2,2,2,2) - bottom-right")
    print("  B at (0,2,1,0) - top-right")
    print("\n" + display.render_board(board))
    
    # Test coordinate conversions
    print("\n" + "=" * 60)
    print("Testing coordinate conversions:")
    test_coords = [
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (2, 2, 2, 2),
        (0, 2, 1, 0),
        (2, 0, 0, 2)
    ]
    
    for w, x, y, z in test_coords:
        row, col = display.coord_to_grid(w, x, y, z)
        w2, x2, y2, z2 = display.grid_to_coord(row, col)
        status = "✓" if (w, x, y, z) == (w2, x2, y2, z2) else "✗"
        print(f"  {status} 4D({w},{x},{y},{z}) <-> Grid({row},{col})")


if __name__ == "__main__":
    test_display()

