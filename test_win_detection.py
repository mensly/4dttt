"""
More thorough test of win detection.
"""

from game.core.board import Board
from game.core.win_checker import get_win_checker


def test_horizontal_win():
    """Test winning in one dimension."""
    print("Testing horizontal win (w-axis)...")
    board = Board()
    win_checker = get_win_checker()
    
    # Make 3 moves in a row along w-axis: (0,1,1,1), (1,1,1,1), (2,1,1,1)
    board.make_move('X', 0, 1, 1, 1)
    board.make_move('X', 1, 1, 1, 1)
    board.make_move('X', 2, 1, 1, 1)
    
    winner = win_checker.check_win(board, 2, 1, 1, 1)
    assert winner == 'X', f"Expected X to win, got {winner}"
    print("  ✓ Horizontal win detected correctly")


def test_diagonal_win():
    """Test diagonal win in 4D."""
    print("Testing diagonal win...")
    board = Board()
    win_checker = get_win_checker()
    
    # Try a diagonal: (0,0,0,0), (1,1,1,1), (2,2,2,2)
    board.make_move('O', 0, 0, 0, 0)
    board.make_move('O', 1, 1, 1, 1)
    board.make_move('O', 2, 2, 2, 2)
    
    winner = win_checker.check_win(board, 2, 2, 2, 2)
    assert winner == 'O', f"Expected O to win, got {winner}"
    print("  ✓ Diagonal win detected correctly")


def test_no_win():
    """Test that non-winning positions don't trigger wins."""
    print("Testing no-win scenarios...")
    board = Board()
    win_checker = get_win_checker()
    
    # Scattered moves, no line
    board.make_move('X', 0, 0, 0, 0)
    board.make_move('X', 1, 2, 2, 2)
    board.make_move('X', 2, 1, 0, 1)
    
    winner = win_checker.check_win_all_positions(board)
    assert winner is None, f"Expected no winner, got {winner}"
    print("  ✓ No false wins detected")


def test_opponent_blocking():
    """Test that opponents can't win when blocked."""
    print("Testing opponent blocking...")
    board = Board()
    win_checker = get_win_checker()
    
    # O has 2 in a row, X blocks
    board.make_move('O', 0, 1, 1, 1)
    board.make_move('O', 1, 1, 1, 1)
    board.make_move('X', 2, 1, 1, 1)  # Block
    
    winner = win_checker.check_win(board, 2, 1, 1, 1)
    assert winner != 'O', "O should not win (blocked)"
    print("  ✓ Blocking works correctly")


def test_multiple_winning_lines():
    """Test positions that could be part of multiple lines."""
    print("Testing multiple potential winning lines...")
    board = Board()
    win_checker = get_win_checker()
    
    # Center position can be part of many lines
    center = (1, 1, 1, 1)
    
    # Make a winning line through center
    board.make_move('X', 0, 1, 1, 1)
    board.make_move('X', 1, 1, 1, 1)
    board.make_move('X', 2, 1, 1, 1)
    
    winner = win_checker.check_win(board, 1, 1, 1, 1)
    assert winner == 'X', f"Expected X to win through center, got {winner}"
    print("  ✓ Multiple line detection works")


def run_tests():
    """Run all win detection tests."""
    print("=" * 60)
    print("WIN DETECTION TESTS")
    print("=" * 60 + "\n")
    
    tests = [
        test_horizontal_win,
        test_diagonal_win,
        test_no_win,
        test_opponent_blocking,
        test_multiple_winning_lines
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)

