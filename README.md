# 4D Tic-Tac-Toe

A 4D Tic-Tac-Toe game played on a 3×3×3×3 hypercube (81 positions total). Supports up to 5 players, with AI bots for training and gameplay.

## Phase 1: Python Offline Script (Complete)

### Features
- 4D board representation (3×3×3×3 hypercube)
- Efficient win checker for all possible 3-point paths
- AI bots (SimpleAI, MinimaxAI)
- Interactive multiplayer gameplay
- Simulation system for training AI bots
- 9×9 grid display (3×3 grid of 3×3 mini-boards)

### Installation

```bash
# No external dependencies required for Phase 1
python3 main.py
```

### Usage

#### Interactive Game
```bash
python main.py
```

#### Run Simulations
```bash
python simulate.py
```

## Phase 2: Hosted Web Game (In Progress)

### Features (Planned)
- Python FastAPI backend
- React frontend
- Room-based multiplayer with code-based joining
- Database persistence (SQLite/PostgreSQL)
- Bot filling for incomplete games
- Dual display: 9×9 grid and 3D rotatable tesseract

### Project Structure

```
4dttt/
├── game/                   # Core game logic (shared between phases)
│   ├── core/              # Board, win checker, game state
│   ├── display/           # Display modules
│   └── ai/                # AI bot implementations
├── main.py                # Phase 1: Interactive game
├── simulate.py            # Phase 1: Simulation system
├── backend/               # Phase 2: FastAPI backend (planned)
└── frontend/              # Phase 2: React frontend (planned)
```

