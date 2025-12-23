"""
AI Training script for 4D Tic-Tac-Toe.
Runs simulations, collects training data, and can train AI models.
"""

import json
import time
from typing import List, Dict, Any
from simulate import run_simulation, collect_statistics, print_statistics
from game.core.game import Game
from game.ai.simple_ai import SimpleAI
from game.ai.minimax_ai import MinimaxAI
from game.ai.trainable_ai import TrainableAI


def collect_training_data(num_games: int, ai_config: Dict[str, Any]) -> List[Dict]:
    """
    Collect detailed training data from games.
    
    Args:
        num_games: Number of games to simulate
        ai_config: Configuration for players
        
    Returns:
        List of game data including move sequences
    """
    training_data = []
    
    print(f"Collecting training data from {num_games} games...")
    
    for game_num in range(num_games):
        if (game_num + 1) % 50 == 0:
            print(f"  Progress: {game_num + 1}/{num_games} games...")
        
        game = Game()
        
        # Add players
        ai_players = {}
        for player_config in ai_config.get('players', []):
            player_id = str(uuid.uuid4())
            player_type = player_config.get('type', 'simple')
            symbol = player_config.get('symbol')
            name = player_config.get('name', f"AI-{symbol}")
            
            game.add_player(player_id, name, symbol, is_bot=True)
            
            # Create AI instance
            if player_type == 'minimax':
                ai = MinimaxAI(symbol, name, max_depth=player_config.get('max_depth', 2))
            elif player_type == 'trainable':
                ai = TrainableAI(symbol, name)
            else:
                ai = SimpleAI(symbol, name)
            
            ai_players[player_id] = ai
        
        # Validate minimum players
        if len(game.players) < Game.MIN_PLAYERS:
            continue
        
        # Start game
        if not game.start_game():
            continue
        
        # Play game and collect moves
        game_moves = []
        move_count = 0
        max_moves = ai_config.get('max_moves', 81)
        
        while not game.check_game_over() and move_count < max_moves:
            current_player = game.get_current_player()
            if current_player is None:
                break
            
            player_id = current_player.player_id
            ai = ai_players[player_id]
            
            # Get board state before move
            board_state = game.get_board_copy()
            
            try:
                w, x, y, z = ai.get_move(board_state)
                success, error = game.make_move(player_id, w, x, y, z)
                
                if not success:
                    break
                
                # Record move data
                move_data = {
                    'player_id': player_id,
                    'player_symbol': current_player.symbol,
                    'player_name': current_player.player_name,
                    'move': [w, x, y, z],
                    'move_number': move_count,
                    'board_state': board_state.get_board_state()  # 4D array representation
                }
                game_moves.append(move_data)
                move_count += 1
            except Exception as e:
                break
        
        # Determine outcome
        winner = game.winner
        is_draw = winner is None and len(game.board.get_empty_positions()) == 0
        
        # Calculate rewards for each player
        for move_data in game_moves:
            player_id = move_data['player_id']
            player = next((p for p in game.players if p.player_id == player_id), None)
            
            if winner and winner.player_id == player_id:
                move_data['reward'] = 1.0  # Win
            elif winner and winner.player_id != player_id:
                move_data['reward'] = -0.5  # Loss
            elif is_draw:
                move_data['reward'] = 0.0  # Draw
            else:
                move_data['reward'] = 0.0  # Game not finished
        
        training_data.append({
            'game_number': game_num + 1,
            'winner': winner.player_id if winner else None,
            'winner_symbol': winner.symbol if winner else None,
            'is_draw': is_draw,
            'total_moves': move_count,
            'moves': game_moves
        })
    
    return training_data


def train_with_data(training_data: List[Dict], ai_config: Dict[str, Any]):
    """
    Train AI models using collected training data.
    
    This is a placeholder for future ML implementation.
    Currently just analyzes the data.
    
    Args:
        training_data: Collected training data
        ai_config: AI configuration
    """
    print("\n" + "=" * 60)
    print("TRAINING DATA ANALYSIS")
    print("=" * 60)
    
    # Analyze move patterns
    move_positions = {}
    win_moves = []
    loss_moves = []
    
    for game_data in training_data:
        for move_data in game_data['moves']:
            move = tuple(move_data['move'])
            move_positions[move] = move_positions.get(move, 0) + 1
            
            reward = move_data.get('reward', 0)
            if reward > 0:
                win_moves.append(move)
            elif reward < 0:
                loss_moves.append(move)
    
    print(f"\nTotal moves collected: {sum(len(g['moves']) for g in training_data)}")
    print(f"Unique move positions: {len(move_positions)}")
    print(f"Winning moves: {len(win_moves)}")
    print(f"Losing moves: {len(loss_moves)}")
    
    # Find most common winning moves
    from collections import Counter
    win_move_counts = Counter(win_moves)
    print(f"\nTop 10 most common winning moves:")
    for move, count in win_move_counts.most_common(10):
        print(f"  {move}: {count} times")
    
    # Find most common losing moves (to avoid)
    loss_move_counts = Counter(loss_moves)
    print(f"\nTop 10 most common losing moves (avoid these):")
    for move, count in loss_move_counts.most_common(10):
        print(f"  {move}: {count} times")


def main():
    """Main training function."""
    import uuid
    
    print("=" * 60)
    print("AI TRAINING SESSION")
    print("=" * 60)
    
    # Training configuration
    # You can experiment with different AI types and configurations
    ai_config = {
        'players': [
            {'type': 'simple', 'symbol': 'X', 'name': 'SimpleAI-1'},
            {'type': 'simple', 'symbol': 'O', 'name': 'SimpleAI-2'},
            {'type': 'minimax', 'symbol': 'A', 'name': 'MinimaxAI', 'max_depth': 2},
            {'type': 'simple', 'symbol': 'B', 'name': 'SimpleAI-3'},
            {'type': 'simple', 'symbol': 'C', 'name': 'SimpleAI-4'}
        ],
        'max_moves': 81
    }
    
    # Number of games for training
    num_games = 500
    
    print(f"\nConfiguration:")
    print(f"  Games to simulate: {num_games}")
    print(f"  Players: {len(ai_config['players'])}")
    for player in ai_config['players']:
        print(f"    - {player['name']} ({player['symbol']}) [{player['type']}]")
    
    # Run simulations and collect statistics
    print("\n" + "-" * 60)
    print("Phase 1: Running simulations...")
    print("-" * 60)
    start_time = time.time()
    
    results = run_simulation(num_games, ai_config, output_file='training_results.json')
    
    # Collect and print statistics
    stats = collect_statistics(results)
    print_statistics(stats)
    
    # Save statistics
    with open('training_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Collect detailed training data
    print("\n" + "-" * 60)
    print("Phase 2: Collecting detailed training data...")
    print("-" * 60)
    
    training_data = collect_training_data(num_games, ai_config)
    
    # Save training data
    with open('training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    print(f"\nTraining data saved to training_data.json")
    print(f"  Games: {len(training_data)}")
    print(f"  Total moves: {sum(len(g['moves']) for g in training_data)}")
    
    # Analyze training data
    train_with_data(training_data, ai_config)
    
    elapsed = time.time() - start_time
    print(f"\n" + "=" * 60)
    print(f"Training complete! Total time: {elapsed:.2f} seconds")
    print("=" * 60)
    print("\nFiles created:")
    print("  - training_results.json: Game results")
    print("  - training_stats.json: Statistics")
    print("  - training_data.json: Detailed move data for ML training")


if __name__ == "__main__":
    import uuid  # Import here too for the collect_training_data function
    main()

