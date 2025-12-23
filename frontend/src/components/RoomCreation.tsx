import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomAPI } from '../services/api';
import './RoomCreation.css';

function RoomCreation() {
  const navigate = useNavigate();
  const [playerName, setPlayerName] = useState('');
  const [symbol, setSymbol] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

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
      const response = await roomAPI.create(playerName.trim(), symbol.trim());
      navigate(`/room/${response.room_code}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create room');
      setLoading(false);
    }
  };

  const popularSymbols = ['X', 'O', '⚡', '🔥', '⭐', '🎮', '🏆', '💎'];

  return (
    <div className="container">
      <h1>4D Tic-Tac-Toe</h1>
      <h2>Create Room</h2>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
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
          {loading ? 'Creating...' : 'Create Room'}
        </button>
      </form>

      <div className="button-group" style={{ marginTop: '1rem' }}>
        <button
          type="button"
          onClick={() => navigate('/join')}
          disabled={loading}
          style={{ background: '#6c757d' }}
        >
          Join Existing Room
        </button>
      </div>
    </div>
  );
}

export default RoomCreation;

