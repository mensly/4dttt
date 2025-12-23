"""
Main script for interactive 4D Tic-Tac-Toe game.
Supports multiplayer with human players and AI bots.
"""

import uuid
import sys
from typing import Optional
from game.core.game import Game, GameState
from game.display.grid_display import GridDisplay
from game.ai.simple_ai import SimpleAI
from game.ai.minimax_ai import MinimaxAI


def print_header():
    """Print game header."""
    print("\n" + "=" * 60)
    print("4D TIC-TAC-TOE")
    print("Play on a 3×3×3×3 hypercube (81 positions)")
    print("=" * 60 + "\n")


def get_player_input(prompt: str, valid_options: list = None) -> str:
    """
    Get input from user with optional validation.
    
    Args:
        prompt: Prompt string
        valid_options: Optional list of valid inputs
        
    Returns:
        User input string
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if valid_options is None or user_input in valid_options:
                return user_input
            else:
                print(f"Invalid input. Please choose from: {', '.join(valid_options)}")
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n\nGame interrupted. Goodbye!")
            sys.exit(0)


def setup_game() -> Game:
    """
    Set up a new game with players.
    
    Returns:
        Configured Game instance
    """
    game = Game()
    
    print("Game Setup")
    print("-" * 60)
    
    # Get number of players
    num_players_input = get_player_input(
        "Number of players (1-5): ",
        [str(i) for i in range(1, 6)]
    )
    num_players = int(num_players_input)
    
    # Get player configuration
    for i in range(num_players):
        print(f"\nPlayer {i + 1}:")
        
        player_type = get_player_input(
            "  Type (h=human, s=simple AI, m=minimax AI) [h]: ",
            ['h', 's', 'm', '']
        ) or 'h'
        
        player_name = get_player_input(f"  Name: ")
        
        symbol = get_player_input(f"  Symbol (1-2 characters): ")
        while len(symbol) == 0 or len(symbol) > 2:
            symbol = get_player_input(f"  Symbol must be 1-2 characters. Try again: ")
        
        player_id = str(uuid.uuid4())
        is_bot = player_type in ['s', 'm']
        
        if not game.add_player(player_id, player_name, symbol, is_bot=is_bot):
            print(f"  Error: Could not add player. Symbol might be taken.")
            i -= 1
            continue
        
        print(f"  Added {player_name} ({symbol}) as {'bot' if is_bot else 'human'}")
    
    return game


def get_human_move(game: Game) -> Optional[tuple]:
    """
    Get move input from human player.
    
    Args:
        game: Current game
        
    Returns:
        Tuple (w, x, y, z) or None if invalid
    """
    current_player = game.get_current_player()
    if current_player is None:
        return None
    
    print(f"\n{current_player.player_name}'s turn ({current_player.symbol})")
    print("Enter coordinates as: w x y z (each 0-2)")
    print("Or 'help' for coordinate explanation, 'board' to see board again")
    
    while True:
        user_input = get_player_input("Move: ").strip().lower()
        
        if user_input == 'help':
            print("\nCoordinate explanation:")
            print("  w: Which 3×3 slice (0-2)")
            print("  x: Column group within slice (0-2)")
            print("  y: Row within slice (0-2)")
            print("  z: Column within group (0-2)")
            print("  Example: 1 0 2 1 means slice 1, group 0, row 2, column 1")
            continue
        
        if user_input == 'board':
            display = GridDisplay()
            print(display.render_board(game.get_board_copy()))
            continue
        
        try:
            parts = user_input.split()
            if len(parts) != 4:
                print("Please enter 4 numbers: w x y z")
                continue
            
            w, x, y, z = map(int, parts)
            
            if not (0 <= w <= 2 and 0 <= x <= 2 and 0 <= y <= 2 and 0 <= z <= 2):
                print("All coordinates must be between 0 and 2")
                continue
            
            return (w, x, y, z)
        except ValueError:
            print("Invalid input. Please enter 4 numbers: w x y z")
            continue


def play_game(game: Game):
    """Play the game."""
    display = GridDisplay()
    
    # Start the game
    if not game.start_game():
        print("Error: Could not start game")
        return
    
    # Create AI instances for bot players
    ai_players = {}
    for player in game.players:
        if player.is_bot:
            # Determine AI type based on name (simple heuristic)
            if 'minimax' in player.player_name.lower():
                ai_players[player.player_id] = MinimaxAI(player.symbol, player.player_name, max_depth=2)
            else:
                ai_players[player.player_id] = SimpleAI(player.symbol, player.player_name)
    
    print("\n" + "=" * 60)
    print("GAME STARTED")
    print("=" * 60)
    print(display.render_board(game.get_board_copy()))
    
    # Game loop
    move_number = 0
    while not game.check_game_over():
        current_player = game.get_current_player()
        if current_player is None:
            break
        
        move_number += 1
        print(f"\n--- Move {move_number} ---")
        
        # Get move
        if current_player.is_bot:
            # AI move
            print(f"{current_player.player_name}'s turn ({current_player.symbol}) - AI thinking...")
            ai = ai_players[current_player.player_id]
            board = game.get_board_copy()
            try:
                w, x, y, z = ai.get_move(board)
                print(f"AI chooses: {w} {x} {y} {z}")
            except Exception as e:
                print(f"Error getting AI move: {e}")
                break
        else:
            # Human move
            move = get_human_move(game)
            if move is None:
                continue
            w, x, y, z = move
        
        # Make the move
        success, error = game.make_move(current_player.player_id, w, x, y, z)
        if not success:
            print(f"Error: {error}")
            if not current_player.is_bot:
                continue  # Let human try again
            else:
                break  # AI error, abort
        
        # Display updated board
        last_move = (w, x, y, z)
        winning_line = game.winning_line if game.winner else None
        print(display.render_board(game.get_board_copy(), 
                                   highlight_last_move=last_move,
                                   highlight_winning_line=winning_line))
    
    # Game over
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)
    
    if game.winner:
        print(f"Winner: {game.winner.player_name} ({game.winner.symbol})!")
    else:
        print("Draw! Board is full.")
    
    print(f"Total moves: {len(game.move_history)}")
    print("=" * 60 + "\n")


def main():
    """Main game loop."""
    print_header()
    
    while True:
        print("Options:")
        print("  1. New game")
        print("  2. Exit")
        
        choice = get_player_input("Choose option [1]: ", ['1', '2', '']) or '1'
        
        if choice == '2':
            print("Thanks for playing!")
            break
        
        # Setup and play game
        game = setup_game()
        
        if len(game.players) == 0:
            print("No players added. Returning to menu.")
            continue
        
        play_game(game)


if __name__ == "__main__":
    main()

