import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomAPI } from '../services/api';
import './RoomJoin.css';

function RoomJoin() {
  const navigate = useNavigate();
  const [roomCode, setRoomCode] = useState('');
  const [playerName, setPlayerName] = useState('');
  const [symbol, setSymbol] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!roomCode.trim() || roomCode.length !== 6) {
      setError('Room code must be 6 characters');
      setLoading(false);
      return;
    }

    if (!playerName.trim()) {
      setError('Player name is required');
      setLoading(false);
      return;
    }

    if (!symbol.trim() || symbol.length > 2) {
      setError('Symbol must be 1-2 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await roomAPI.join(roomCode.trim().toUpperCase(), playerName.trim(), symbol.trim());
      navigate(`/room/${response.room_code}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to join room');
      setLoading(false);
    }
  };

  const popularSymbols = ['X', 'O', '⚡', '🔥', '⭐', '🎮', '🏆', '💎'];

  return (
    <div className="container">
      <h1>4D Tic-Tac-Toe</h1>
      <h2>Join Room</h2>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="roomCode">Room Code</label>
          <input
            type="text"
            id="roomCode"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ''))}
            placeholder="Enter 6-character code"
            maxLength={6}
            disabled={loading}
            required
            style={{ fontFamily: 'monospace', letterSpacing: '0.2em', textAlign: 'center' }}
          />
        </div>

        <div className="form-group">
          <label htmlFor="playerName">Player Name</label>
          <input
            type="text"
            id="playerName"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Enter your name"
            maxLength={50}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="symbol">Symbol (1-2 characters)</label>
          <input
            type="text"
            id="symbol"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="X, O, ⚡, etc."
            maxLength={2}
            disabled={loading}
            required
          />
          <div className="symbol-suggestions">
            <span>Quick pick: </span>
            {popularSymbols.map((sym) => (
              <button
                key={sym}
                type="button"
                className="symbol-button"
                onClick={() => setSymbol(sym)}
                disabled={loading}
              >
                {sym}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Joining...' : 'Join Room'}
        </button>
      </form>

      <div className="button-group" style={{ marginTop: '1rem' }}>
        <button
          type="button"
          onClick={() => navigate('/')}
          disabled={loading}
          style={{ background: '#6c757d' }}
        >
          Create New Room
        </button>
      </div>
    </div>
  );
}

export default RoomJoin;

