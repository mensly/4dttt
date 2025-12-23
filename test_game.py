"""
Test script for Phase 1 game functionality.
Tests core game logic, win detection, and basic gameplay.
"""

import sys
from game.core.board import Board
from game.core.win_checker import WinChecker, get_win_checker
from game.core.game import Game, GameState
from game.display.grid_display import GridDisplay
from game.ai.simple_ai import SimpleAI
from game.ai.minimax_ai import MinimaxAI


def test_board():
    """Test basic board functionality."""
    print("Testing Board...")
    board = Board()
    
    # Test valid position
    assert board.is_valid_position(0, 0, 0, 0) == True
    assert board.is_valid_position(2, 2, 2, 2) == True
    assert board.is_valid_position(3, 0, 0, 0) == False
    assert board.is_valid_position(-1, 0, 0, 0) == False
    
    # Test empty board
    assert board.get(1, 1, 1, 1) is None
    assert len(board.get_empty_positions()) == 81
    
    # Test making moves
    assert board.make_move('X', 1, 1, 1, 1) == True
    assert board.get(1, 1, 1, 1) == 'X'
    assert len(board.get_empty_positions()) == 80
    assert board.is_valid_move(1, 1, 1, 1) == False  # Already occupied
    
    # Test invalid move
    assert board.make_move('O', 1, 1, 1, 1) == False  # Position taken
    
    # Test board copy
    board2 = board.copy()
    assert board2.get(1, 1, 1, 1) == 'X'
    board2.make_move('O', 0, 0, 0, 0)
    assert board.get(0, 0, 0, 0) is None  # Original unchanged
    
    print("  ✓ Board tests passed")


def test_win_checker():
    """Test win detection."""
    print("Testing Win Checker...")
    win_checker = get_win_checker()
    
    # Check that winning lines are computed
    lines = win_checker.get_all_winning_lines()
    assert len(lines) > 0
    print(f"  Found {len(lines)} winning lines")
    
    # Test a simple win (3 in a row along w-axis)
    board = Board()
    board.make_move('X', 0, 1, 1, 1)
    board.make_move('X', 1, 1, 1, 1)
    board.make_move('X', 2, 1, 1, 1)
    
    winner = win_checker.check_win(board, 2, 1, 1, 1)
    assert winner == 'X', f"Expected 'X' to win, got {winner}"
    
    # Test no win
    board2 = Board()
    board2.make_move('X', 0, 0, 0, 0)
    board2.make_move('O', 1, 1, 1, 1)
    board2.make_move('X', 2, 2, 2, 2)
    
    winner = win_checker.check_win(board2, 2, 2, 2, 2)
    assert winner is None
    
    print("  ✓ Win checker tests passed")


def test_game():
    """Test game state management."""
    print("Testing Game...")
    game = Game()
    
    # Test initial state
    assert game.state == GameState.WAITING
    assert len(game.players) == 0
    
    # Test adding players (minimum 4 required)
    assert game.add_player("p1", "Alice", "X") == True
    assert game.add_player("p2", "Bob", "O") == True
    assert game.add_player("p3", "Charlie", "A") == True
    assert game.add_player("p4", "Dave", "B") == True
    assert len(game.players) == 4
    
    # Test duplicate symbol rejection
    assert game.add_player("p5", "Eve", "X") == False
    
    # Test starting game with minimum players
    assert game.start_game() == True
    
    # Test that game won't start with less than 4 players
    game2 = Game()
    game2.add_player("p1", "Alice", "X")
    game2.add_player("p2", "Bob", "O")
    game2.add_player("p3", "Charlie", "A")
    assert game2.start_game() == False  # Only 3 players, should fail
    assert game.state == GameState.PLAYING
    assert game.get_current_player().player_id == "p1"
    
    # Test making moves
    success, error = game.make_move("p1", 1, 1, 1, 1)
    assert success == True
    assert game.get_current_player().player_id == "p2"
    
    # Test invalid move (wrong player)
    success, error = game.make_move("p1", 0, 0, 0, 0)
    assert success == False
    
    # Test invalid position
    success, error = game.make_move("p2", 5, 0, 0, 0)
    assert success == False
    
    print("  ✓ Game tests passed")


def test_display():
    """Test display functionality."""
    print("Testing Display...")
    display = GridDisplay()
    board = Board()
    
    # Test coordinate conversion
    row, col = display.coord_to_grid(0, 0, 0, 0)
    assert row == 0 and col == 0
    
    row, col = display.coord_to_grid(1, 1, 1, 1)
    assert row == 4 and col == 4
    
    w, x, y, z = display.grid_to_coord(4, 4)
    assert (w, x, y, z) == (1, 1, 1, 1)
    
    # Test rendering
    board.make_move('X', 1, 1, 1, 1)
    board.make_move('O', 0, 0, 0, 0)
    rendered = display.render_board(board)
    assert 'X' in rendered
    assert 'O' in rendered
    
    print("  ✓ Display tests passed")


def test_ai():
    """Test AI functionality."""
    print("Testing AI...")
    board = Board()
    
    # Test SimpleAI
    ai = SimpleAI('X', "TestAI")
    assert ai.get_symbol() == 'X'
    assert ai.get_name() == "TestAI"
    
    # AI should be able to make a move on empty board
    move = ai.get_move(board)
    assert len(move) == 4
    w, x, y, z = move
    assert 0 <= w <= 2 and 0 <= x <= 2 and 0 <= y <= 2 and 0 <= z <= 2
    
    # Test MinimaxAI
    ai2 = MinimaxAI('O', "MinimaxAI", max_depth=1)
    move2 = ai2.get_move(board)
    assert len(move2) == 4
    
    print("  ✓ AI tests passed")


def test_full_game():
    """Test a complete game with AI players."""
    print("Testing full game simulation...")
    game = Game()
    
    # Add AI players (minimum 4 required)
    game.add_player("ai1", "Simple1", "X", is_bot=True)
    game.add_player("ai2", "Simple2", "O", is_bot=True)
    game.add_player("ai3", "Simple3", "A", is_bot=True)
    game.add_player("ai4", "Simple4", "B", is_bot=True)
    
    assert game.start_game() == True
    
    # Create AI instances
    ai1 = SimpleAI('X', "Simple1")
    ai2 = SimpleAI('O', "Simple2")
    ai3 = SimpleAI('A', "Simple3")
    ai4 = SimpleAI('B', "Simple4")
    ai_players = {"ai1": ai1, "ai2": ai2, "ai3": ai3, "ai4": ai4}
    
    # Play a few moves
    move_count = 0
    max_moves = 10  # Limit for testing
    
    while not game.check_game_over() and move_count < max_moves:
        current_player = game.get_current_player()
        if current_player is None:
            break
        
        player_id = current_player.player_id
        ai = ai_players[player_id]
        
        board = game.get_board_copy()
        w, x, y, z = ai.get_move(board)
        success, error = game.make_move(player_id, w, x, y, z)
        
        if not success:
            print(f"  Warning: Move failed: {error}")
            break
        
        move_count += 1
    
    assert move_count > 0, "Should have made at least one move"
    print(f"  ✓ Full game test passed ({move_count} moves made)")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 1 TEST SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        test_board,
        test_win_checker,
        test_game,
        test_display,
        test_ai,
        test_full_game
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
    success = run_all_tests()
    sys.exit(0 if success else 1)

