"""
Test script to compare LearnedAI with SimpleAI using training data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game.core.game import Game
from game.ai.simple_ai import SimpleAI
from game.ai.learned_ai import LearnedAI


def test_ai_comparison(num_games: int = 100):
    """Compare LearnedAI vs SimpleAI performance."""
    print("=" * 60)
    print("AI COMPARISON TEST")
    print("=" * 60)
    
    # Check if training data exists
    training_data_path = Path('training_data.json')
    if not training_data_path.exists():
        print("Error: training_data.json not found!")
        print("  Please run train_ai.py first to generate training data.")
        return
    
    print(f"\nRunning {num_games} games to compare AIs...")
    print("  LearnedAI (using training data) vs SimpleAI\n")
    
    learned_wins = 0
    simple_wins = 0
    draws = 0
    
    for game_num in range(num_games):
        if (game_num + 1) % 20 == 0:
            print(f"  Progress: {game_num + 1}/{num_games} games...")
        
        game = Game()
        
        # Add players
        learned_ai = LearnedAI('X', 'LearnedAI', str(training_data_path))
        simple_ai = SimpleAI('O', 'SimpleAI')
        
        game.add_player('p1', 'LearnedAI', 'X', is_bot=True)
        game.add_player('p2', 'SimpleAI', 'O', is_bot=True)
        game.add_player('p3', 'SimpleAI-2', 'A', is_bot=True)
        game.add_player('p4', 'SimpleAI-3', 'B', is_bot=True)
        
        if not game.start_game():
            continue
        
        ai_instances = {
            'p1': learned_ai,
            'p2': simple_ai,
            'p3': SimpleAI('A', 'SimpleAI-2'),
            'p4': SimpleAI('B', 'SimpleAI-3'),
        }
        
        # Play game
        max_moves = 81
        move_count = 0
        
        while not game.check_game_over() and move_count < max_moves:
            current_player = game.get_current_player()
            if current_player is None:
                break
            
            player_id = current_player.player_id
            ai = ai_instances[player_id]
            
            try:
                board = game.get_board_copy()
                w, x, y, z = ai.get_move(board)
                success, error = game.make_move(player_id, w, x, y, z)
                
                if not success:
                    break
                
                move_count += 1
            except Exception as e:
                break
        
        # Check winner
        if game.winner:
            if game.winner.player_id == 'p1':
                learned_wins += 1
            else:
                simple_wins += 1
        else:
            draws += 1
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"LearnedAI wins: {learned_wins} ({learned_wins/num_games*100:.1f}%)")
    print(f"SimpleAI wins: {simple_wins} ({simple_wins/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
    print("=" * 60)
    
    if learned_wins > simple_wins:
        print("\n✓ LearnedAI performed better!")
    elif simple_wins > learned_wins:
        print("\n✗ SimpleAI performed better (may need more training data)")
    else:
        print("\n~ AIs performed similarly")


if __name__ == "__main__":
    test_ai_comparison(100)

