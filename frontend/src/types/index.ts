/**
 * Type definitions for the application
 */

export interface Player {
  player_id: string;
  player_name: string;
  symbol: string;
  is_bot: boolean;
  joined_at: string;
}

export interface RoomStatus {
  room_code: string;
  state: 'waiting' | 'playing' | 'finished';
  players: Player[];
  host_player_id: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  winner_player_id: string | null;
}

export interface GameState {
  room_code: string;
  state: 'waiting' | 'playing' | 'finished';
  current_player_id: string | null;
  board_state: (string | null)[][][][]; // 4D array [w][x][y][z]
  move_count: number;
  winner_player_id: string | null;
  is_draw: boolean;
  players?: Player[];
}

export interface MoveResponse {
  success: boolean;
  error: string | null;
  game_state: string;
  winner: string | null;
}

export interface RoomCreateResponse {
  room_code: string;
  player_id: string;
  token: string;
}

export interface RoomJoinResponse {
  room_code: string;
  player_id: string;
  token: string;
}

