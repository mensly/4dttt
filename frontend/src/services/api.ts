/**
 * API service for communicating with the backend
 */

import axios from 'axios';
import { API_ENDPOINTS } from '../utils/constants';
import type { RoomStatus, GameState, MoveResponse, RoomCreateResponse, RoomJoinResponse } from '../types';

// Create axios instance
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get auth headers
const getAuthHeaders = (token: string) => ({
  'Authorization': `Bearer ${token}`,
  'X-Player-ID': localStorage.getItem('playerId') || '',
});

/**
 * Room API functions
 */
export const roomAPI = {
  create: async (playerName: string, symbol: string): Promise<RoomCreateResponse> => {
    const response = await api.post<RoomCreateResponse>(API_ENDPOINTS.ROOMS.CREATE, {
      player_name: playerName,
      symbol: symbol,
    });
    // Store token and player ID
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('playerId', response.data.player_id);
    }
    return response.data;
  },

  join: async (roomCode: string, playerName: string, symbol: string): Promise<RoomJoinResponse> => {
    const response = await api.post<RoomJoinResponse>(API_ENDPOINTS.ROOMS.JOIN, {
      room_code: roomCode.toUpperCase(),
      player_name: playerName,
      symbol: symbol,
    });
    // Store token and player ID
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('playerId', response.data.player_id);
    }
    return response.data;
  },

  getStatus: async (roomCode: string): Promise<RoomStatus> => {
    const response = await api.get<RoomStatus>(API_ENDPOINTS.ROOMS.STATUS(roomCode.toUpperCase()));
    return response.data;
  },

  start: async (roomCode: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(API_ENDPOINTS.ROOMS.START(roomCode.toUpperCase()));
    return response.data;
  },

  getBoard: async (roomCode: string): Promise<GameState> => {
    const response = await api.get<GameState>(API_ENDPOINTS.ROOMS.BOARD(roomCode.toUpperCase()));
    return response.data;
  },

  addBot: async (roomCode: string): Promise<{ success: boolean; message: string; bot: any }> => {
    const response = await api.post(API_ENDPOINTS.ROOMS.ADD_BOT(roomCode.toUpperCase()));
    return response.data;
  },
};

/**
 * Game API functions
 */
export const gameAPI = {
  makeMove: async (roomCode: string, w: number, x: number, y: number, z: number): Promise<MoveResponse> => {
    const token = localStorage.getItem('token');
    const playerId = localStorage.getItem('playerId');
    
    if (!token || !playerId) {
      throw new Error('Not authenticated');
    }

    const response = await api.post<MoveResponse>(
      API_ENDPOINTS.GAME.MOVE(roomCode.toUpperCase()),
      { w, x, y, z },
      {
        headers: getAuthHeaders(token),
      }
    );
    return response.data;
  },

  getState: async (roomCode: string): Promise<GameState> => {
    const response = await api.get<GameState>(API_ENDPOINTS.GAME.STATE(roomCode.toUpperCase()));
    return response.data;
  },

  getHistory: async (roomCode: string): Promise<{ room_code: string; moves: any[]; total_moves: number }> => {
    const response = await api.get(API_ENDPOINTS.GAME.HISTORY(roomCode.toUpperCase()));
    return response.data;
  },
};

/**
 * Health check
 */
export const healthCheck = async (): Promise<{ status: string; service: string; version: string }> => {
  const response = await api.get(API_ENDPOINTS.HEALTH);
  return response.data;
};

