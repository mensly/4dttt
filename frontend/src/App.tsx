import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RoomCreation from './components/RoomCreation';
import RoomJoin from './components/RoomJoin';
import RoomLobby from './components/RoomLobby';
import GameBoard from './components/GameBoard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<RoomCreation />} />
          <Route path="/join" element={<RoomJoin />} />
          <Route path="/room/:roomCode" element={<RoomLobby />} />
          <Route path="/game/:roomCode" element={<GameBoard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

