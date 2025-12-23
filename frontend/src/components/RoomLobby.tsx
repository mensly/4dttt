import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { roomAPI } from '../services/api';
import { GAME_CONSTANTS } from '../utils/constants';
import type { RoomStatus } from '../types';
import './RoomLobby.css';

function RoomLobby() {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [roomStatus, setRoomStatus] = useState<RoomStatus | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [addingBot, setAddingBot] = useState(false);

  const playerId = localStorage.getItem('playerId');

  useEffect(() => {
    if (!roomCode) return;
    fetchRoomStatus();
    // Poll for updates every 2 seconds
    const interval = setInterval(fetchRoomStatus, 2000);
    return () => clearInterval(interval);
  }, [roomCode]);

  const fetchRoomStatus = async () => {
    if (!roomCode) return;
    try {
      const status = await roomAPI.getStatus(roomCode);
      setRoomStatus(status);
      setLoading(false);
      setError('');

      // If game started, navigate to game board
      if (status.state === 'playing') {
        navigate(`/game/${roomCode}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load room status');
      setLoading(false);
    }
  };

  const handleStartGame = async () => {
    if (!roomCode) return;
    setStarting(true);
    setError('');
    try {
      await roomAPI.start(roomCode);
      navigate(`/game/${roomCode}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start game');
      setStarting(false);
    }
  };

  const handleCopyCode = () => {
    if (!roomCode) return;
    navigator.clipboard.writeText(roomCode);
    alert('Room code copied to clipboard!');
  };

  const handleAddBot = async () => {
    if (!roomCode) return;
    setAddingBot(true);
    setError('');
    try {
      await roomAPI.addBot(roomCode);
      // Refresh room status to show new bot
      await fetchRoomStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to add bot');
    } finally {
      setAddingBot(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading room...</div>
      </div>
    );
  }

  if (error && !roomStatus) {
    return (
      <div className="container">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  if (!roomCode || !roomStatus) {
    return (
      <div className="container">
        <div className="error">Room code missing</div>
        <button onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  const canStart = roomStatus.players.length >= GAME_CONSTANTS.MIN_PLAYERS;
  const isHost = roomStatus.host_player_id === playerId;

  return (
    <div className="container">
      <h1>Room Lobby</h1>

      <div className="room-code-display">
        <div className="room-code-label">Room Code</div>
        <div className="room-code" onClick={handleCopyCode} title="Click to copy">
          {roomCode}
        </div>
        <button
          type="button"
          onClick={handleCopyCode}
          style={{ marginTop: '0.5rem', padding: '0.5rem' }}
        >
          Copy Code
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="player-list-section">
        <h2>Players ({roomStatus.players.length}/{GAME_CONSTANTS.MAX_PLAYERS})</h2>
        <ul className="player-list">
          {roomStatus.players.map((player) => (
            <li key={player.player_id} className="player-item">
              <div>
                <span className="player-symbol">{player.symbol}</span>
                <span>{player.player_name}</span>
                {player.is_bot && <span className="bot-badge">Bot</span>}
              </div>
              {player.player_id === playerId && <span className="you-badge">You</span>}
            </li>
          ))}
        </ul>
      </div>

      {!canStart && (
        <div className="info">
          Need at least {GAME_CONSTANTS.MIN_PLAYERS} players to start. 
          Current: {roomStatus.players.length}
        </div>
      )}

      {roomStatus.state === 'waiting' && roomStatus.players.length < GAME_CONSTANTS.MAX_PLAYERS && (
        <button
          onClick={handleAddBot}
          disabled={addingBot}
          style={{ background: '#28a745', marginBottom: '1rem' }}
        >
          {addingBot ? 'Adding Bot...' : 'Add AI Bot'}
        </button>
      )}

      {(isHost || canStart) && (
        <button
          onClick={handleStartGame}
          disabled={!canStart || starting || roomStatus.state !== 'waiting'}
        >
          {starting ? 'Starting...' : 'Start Game'}
        </button>
      )}

      {roomStatus.state !== 'waiting' && (
        <div className="info">
          Game is {roomStatus.state === 'playing' ? 'in progress' : 'finished'}
        </div>
      )}
    </div>
  );
}

export default RoomLobby;

