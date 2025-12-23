import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { gameAPI } from '../services/api';
import type { GameState } from '../types';
import GridView from './GridView';
import './GameBoard.css';

function GameBoard() {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submittingMove, setSubmittingMove] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'tesseract'>('grid');

  const playerId = localStorage.getItem('playerId');

  useEffect(() => {
    if (!roomCode) return;
    fetchGameState();
    // Poll for updates every 1 second while game is playing
    // Skip polling if we're submitting a move to avoid race conditions
    const interval = setInterval(() => {
      if (!submittingMove) {
        fetchGameState();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [roomCode, submittingMove]);

  const fetchGameState = async () => {
    if (!roomCode) return;
    try {
      const state = await gameAPI.getState(roomCode);
      setGameState(state);
      setLoading(false);
      setError('');

      // If game finished, might want to show result
      if (state.state === 'finished') {
        // Could show winner/draw message
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load game state');
      setLoading(false);
    }
  };

  const handleCellClick = async (w: number, x: number, y: number, z: number) => {
    console.log('GameBoard handleCellClick called', { w, x, y, z, roomCode, playerId, gameState: gameState?.state, currentPlayerId: gameState?.current_player_id });
    
    if (!roomCode) {
      console.log('No room code');
      return;
    }
    if (submittingMove) {
      console.log('Already submitting move');
      return;
    }
    if (!gameState) {
      console.log('No game state');
      return;
    }
    if (gameState.state !== 'playing') {
      console.log('Game not in playing state:', gameState.state);
      setError('Game is not in playing state');
      return;
    }
    if (gameState.current_player_id !== playerId) {
      console.log('Not your turn. Current:', gameState.current_player_id, 'Yours:', playerId);
      setError('Not your turn!');
      return;
    }

    // Check if cell is already occupied
    if (gameState.board_state[w][x][y][z] !== null && gameState.board_state[w][x][y][z] !== undefined && gameState.board_state[w][x][y][z] !== '') {
      console.log('Cell already occupied:', gameState.board_state[w][x][y][z]);
      setError('This cell is already occupied!');
      return;
    }

    console.log('Making move...');
    setSubmittingMove(true);
    setError('');

    try {
      await gameAPI.makeMove(roomCode, w, x, y, z);
      console.log('Move API call successful, refreshing game state...');
      // Refresh game state after move
      await fetchGameState();
      console.log('Game state refreshed');
    } catch (err: any) {
      console.error('Move failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to make move');
      // Still refresh game state even on error, in case the move actually went through
      try {
        await fetchGameState();
      } catch (refreshErr) {
        console.error('Failed to refresh game state after error:', refreshErr);
      }
    } finally {
      // Always reset submittingMove, even if there's an error
      console.log('Resetting submittingMove to false');
      setSubmittingMove(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading game...</div>
      </div>
    );
  }

  if (error && !gameState) {
    return (
      <div className="container">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  if (!gameState || !roomCode) {
    return (
      <div className="container">
        <div className="error">Game not found</div>
        <button onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  const isMyTurn = gameState.current_player_id === playerId;
  const currentPlayer = gameState.players?.find(p => p.player_id === gameState.current_player_id);
  const currentPlayerDisplay = currentPlayer 
    ? `${currentPlayer.player_name} (${currentPlayer.symbol})`
    : 'Unknown';
  const winnerPlayer = gameState.winner_player_id 
    ? gameState.players?.find(p => p.player_id === gameState.winner_player_id)
    : null;
  const winnerDisplay = winnerPlayer 
    ? `${winnerPlayer.player_name} (${winnerPlayer.symbol})`
    : 'Unknown';

  return (
    <div className="game-container">
      <div className="game-header">
        <h1>4D Tic-Tac-Toe</h1>
        <div className="room-code-small">Room: {roomCode}</div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="game-status">
        {gameState.state === 'playing' && (
          <div className={`turn-indicator ${isMyTurn ? 'your-turn' : 'opponent-turn'}`}>
            {isMyTurn ? 'Your Turn!' : `${currentPlayerDisplay}'s Turn`}
          </div>
        )}
        {gameState.state === 'finished' && (
          <div className="game-finished">
            {gameState.winner_player_id ? (
              gameState.winner_player_id === playerId ? (
                <div className="winner-message">You Won! 🎉</div>
              ) : (
                <div className="loser-message">Game Over - {winnerDisplay} Won! 🏆</div>
              )
            ) : (
              <div className="draw-message">Draw! Board is full.</div>
            )}
          </div>
        )}
      </div>

      <div className="view-mode-toggle">
        <button
          className={viewMode === 'grid' ? 'active' : ''}
          onClick={() => setViewMode('grid')}
        >
          9×9 Grid
        </button>
        <button
          className={viewMode === 'tesseract' ? 'active' : ''}
          onClick={() => setViewMode('tesseract')}
          disabled={true} // TODO: Implement tesseract view
        >
          3D Tesseract
        </button>
      </div>

      <div className="board-container">
        {viewMode === 'grid' ? (
          <GridView
            boardState={gameState.board_state}
            onCellClick={handleCellClick}
            disabled={submittingMove || !isMyTurn || gameState.state !== 'playing'}
            currentPlayerId={playerId || ''}
            players={gameState.players || []}
          />
        ) : (
          <div className="coming-soon">
            3D Tesseract view coming soon!
          </div>
        )}
      </div>
      
      {/* Debug info */}
      <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '6px', fontSize: '0.9rem' }}>
        <div>Game State: {gameState.state}</div>
        <div>Current Player ID: {gameState.current_player_id || 'None'}</div>
        <div>Your Player ID: {playerId || 'None'}</div>
        <div>Is My Turn: {isMyTurn ? 'Yes' : 'No'}</div>
        <div>Submitting Move: {submittingMove ? 'Yes' : 'No'}</div>
        <div>Disabled: {submittingMove || !isMyTurn || gameState.state !== 'playing' ? 'Yes' : 'No'}</div>
      </div>
      
      {gameState.state === 'playing' && !isMyTurn && (
        <div className="info" style={{ marginTop: '1rem' }}>
          Waiting for {currentPlayerName}'s turn...
        </div>
      )}

      <div className="game-info">
        <div>Moves: {gameState.move_count}</div>
        {gameState.players && (
          <div className="player-list-small">
            {gameState.players.map(p => (
              <span key={p.player_id} className={`player-badge ${p.player_id === playerId ? 'you' : ''}`}>
                {p.symbol} {p.player_name}
              </span>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={() => navigate('/')}
        style={{ marginTop: '1rem', background: '#6c757d' }}
      >
        Leave Game
      </button>
    </div>
  );
}

export default GameBoard;

