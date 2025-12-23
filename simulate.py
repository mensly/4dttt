"""
Simulation script for training AI bots.
Runs multiple games and collects statistics.
"""

import json
import csv
import time
import uuid
from typing import List, Dict, Any
from game.core.game import Game
from game.ai.simple_ai import SimpleAI
from game.ai.minimax_ai import MinimaxAI


def run_simulation(num_games: int, ai_config: Dict[str, Any], output_file: str = None) -> List[Dict]:
    """
    Run a simulation of multiple games.
    
    Args:
        num_games: Number of games to simulate
        ai_config: Configuration dict with keys:
            - 'players': List of dicts with 'type' ('simple' or 'minimax'), 'symbol', 'name'
            - 'max_moves': Maximum moves per game (optional, defaults to 81)
        output_file: Optional file path to save results as JSON
        
    Returns:
        List of game result dictionaries
    """
    results = []
    
    print(f"Starting simulation: {num_games} games with {len(ai_config.get('players', []))} players")
    
    for game_num in range(num_games):
        if (game_num + 1) % 10 == 0:
            print(f"Completed {game_num + 1}/{num_games} games...")
        
        game = Game()
        
        # Add players
        ai_players = []
        for player_config in ai_config.get('players', []):
            player_id = str(uuid.uuid4())
            player_type = player_config.get('type', 'simple')
            symbol = player_config.get('symbol')
            name = player_config.get('name', f"AI-{symbol}")
            
            game.add_player(player_id, name, symbol, is_bot=True)
            
            # Create AI instance
            if player_type == 'minimax':
                ai = MinimaxAI(symbol, name, max_depth=player_config.get('max_depth', 2))
            else:
                ai = SimpleAI(symbol, name)
            
            ai_players.append((player_id, ai))
        
        # Validate minimum players
        if len(game.players) < Game.MIN_PLAYERS:
            print(f"Warning: Game {game_num + 1} has only {len(game.players)} players, need at least {Game.MIN_PLAYERS}. Skipping.")
            continue
        
        # Start game
        if not game.start_game():
            print(f"Warning: Failed to start game {game_num + 1}")
            continue
        
        # Play game
        start_time = time.time()
        max_moves = ai_config.get('max_moves', 81)
        move_count = 0
        
        while not game.check_game_over() and move_count < max_moves:
            current_player = game.get_current_player()
            if current_player is None:
                break
            
            # Find AI for current player
            player_id, ai = next((pid, a) for pid, a in ai_players if pid == current_player.player_id)
            
            # Get move from AI
            try:
                board = game.get_board_copy()
                w, x, y, z = ai.get_move(board)
                success, error = game.make_move(player_id, w, x, y, z)
                
                if not success:
                    print(f"Warning: AI move failed: {error}")
                    break
                
                move_count += 1
            except Exception as e:
                print(f"Error getting AI move: {e}")
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Collect results
        winner = game.winner
        result = {
            'game_number': game_num + 1,
            'winner': winner.player_id if winner else None,
            'winner_symbol': winner.symbol if winner else None,
            'winner_name': winner.player_name if winner else None,
            'move_count': move_count,
            'duration_seconds': duration,
            'players': [{'id': p.player_id, 'name': p.player_name, 'symbol': p.symbol} 
                       for p in game.players],
            'is_draw': winner is None and len(game.board.get_empty_positions()) == 0
        }
        results.append(result)
    
    # Save results if output file specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")
    
    return results


def collect_statistics(results: List[Dict]) -> Dict[str, Any]:
    """
    Collect statistics from simulation results.
    
    Args:
        results: List of game result dictionaries
        
    Returns:
        Dictionary with statistics
    """
    if not results:
        return {}
    
    total_games = len(results)
    wins_by_symbol = {}
    wins_by_name = {}
    total_moves = 0
    total_duration = 0.0
    draws = 0
    
    for result in results:
        if result.get('is_draw'):
            draws += 1
        else:
            symbol = result.get('winner_symbol')
            name = result.get('winner_name')
            if symbol:
                wins_by_symbol[symbol] = wins_by_symbol.get(symbol, 0) + 1
            if name:
                wins_by_name[name] = wins_by_name.get(name, 0) + 1
        
        total_moves += result.get('move_count', 0)
        total_duration += result.get('duration_seconds', 0.0)
    
    stats = {
        'total_games': total_games,
        'draws': draws,
        'wins_by_symbol': wins_by_symbol,
        'wins_by_name': wins_by_name,
        'win_rates_by_symbol': {symbol: count / total_games 
                               for symbol, count in wins_by_symbol.items()},
        'win_rates_by_name': {name: count / total_games 
                             for name, count in wins_by_name.items()},
        'average_moves_per_game': total_moves / total_games if total_games > 0 else 0,
        'average_duration_seconds': total_duration / total_games if total_games > 0 else 0,
        'total_duration_seconds': total_duration
    }
    
    return stats


def print_statistics(stats: Dict[str, Any]):
    """Print statistics in a readable format."""
    print("\n" + "=" * 60)
    print("SIMULATION STATISTICS")
    print("=" * 60)
    print(f"Total games: {stats.get('total_games', 0)}")
    print(f"Draws: {stats.get('draws', 0)}")
    print(f"\nWin counts by symbol:")
    for symbol, count in stats.get('wins_by_symbol', {}).items():
        rate = stats.get('win_rates_by_symbol', {}).get(symbol, 0) * 100
        print(f"  {symbol}: {count} wins ({rate:.1f}%)")
    print(f"\nWin counts by name:")
    for name, count in stats.get('wins_by_name', {}).items():
        rate = stats.get('win_rates_by_name', {}).get(name, 0) * 100
        print(f"  {name}: {count} wins ({rate:.1f}%)")
    print(f"\nAverage moves per game: {stats.get('average_moves_per_game', 0):.1f}")
    print(f"Average duration per game: {stats.get('average_duration_seconds', 0):.3f} seconds")
    print(f"Total simulation duration: {stats.get('total_duration_seconds', 0):.2f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    # Example simulation configuration (minimum 4 players)
    ai_config = {
        'players': [
            {'type': 'simple', 'symbol': 'X', 'name': 'SimpleAI-1'},
            {'type': 'simple', 'symbol': 'O', 'name': 'SimpleAI-2'},
            {'type': 'minimax', 'symbol': 'A', 'name': 'MinimaxAI', 'max_depth': 2},
            {'type': 'simple', 'symbol': 'B', 'name': 'SimpleAI-3'},
            {'type': 'simple', 'symbol': 'C', 'name': 'SimpleAI-4'}  # Optional 5th player
        ],
        'max_moves': 81
    }
    
    # Run simulation
    num_games = 100
    print(f"Running {num_games} games...")
    results = run_simulation(num_games, ai_config, output_file='simulation_results.json')
    
    # Collect and print statistics
    stats = collect_statistics(results)
    print_statistics(stats)
    
    # Save statistics
    with open('simulation_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStatistics saved to simulation_stats.json")

