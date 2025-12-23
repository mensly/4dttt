/**
 * API endpoints and constants
 */

export const API_BASE_URL = '/api';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  ROOMS: {
    CREATE: `${API_BASE_URL}/rooms/create`,
    JOIN: `${API_BASE_URL}/rooms/join`,
    STATUS: (code: string) => `${API_BASE_URL}/rooms/${code}/status`,
    START: (code: string) => `${API_BASE_URL}/rooms/${code}/start`,
    BOARD: (code: string) => `${API_BASE_URL}/rooms/${code}/board`,
    ADD_BOT: (code: string) => `${API_BASE_URL}/rooms/${code}/add-bot`,
  },
  GAME: {
    MOVE: (code: string) => `${API_BASE_URL}/game/${code}/move`,
    STATE: (code: string) => `${API_BASE_URL}/game/${code}/state`,
    HISTORY: (code: string) => `${API_BASE_URL}/game/${code}/history`,
  },
};

export const GAME_CONSTANTS = {
  MIN_PLAYERS: 4,
  MAX_PLAYERS: 5,
  BOARD_SIZE: 3,
  TOTAL_POSITIONS: 81, // 3^4
} as const;

