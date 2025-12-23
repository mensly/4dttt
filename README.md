# 4D Tic-Tac-Toe

A 4D Tic-Tac-Toe game played on a 3×3×3×3 hypercube (81 positions total). Supports 4-5 players (minimum 4 required), with AI bots for training and gameplay.

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

## Phase 2: Hosted Web Game

### Features
- Python FastAPI backend
- React TypeScript frontend
- Room-based multiplayer with code-based joining
- Database persistence (SQLite/PostgreSQL)
- Bot filling for incomplete games
- 9×9 grid display

### Setup

#### Backend Setup

1. **Install Python dependencies:**
```bash
source .venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

2. **Start the backend server:**
```bash
# Option 1: Using Python directly
python backend/main.py

# Option 2: Using uvicorn directly
uvicorn backend.main:app --reload --port 8000
```

The backend will run on `http://localhost:8000`

#### Frontend Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Start the frontend dev server:**
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

### Development Workflow

1. Start backend: `python backend/main.py` (or `uvicorn backend.main:app --reload`)
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3000`

### Project Structure

```
4dttt/
├── game/                   # Core game logic (shared between phases)
│   ├── core/              # Board, win checker, game state
│   ├── display/           # Display modules
│   └── ai/                # AI bot implementations
├── backend/               # Phase 2: FastAPI backend
│   ├── api/routes/        # API endpoints
│   ├── core/              # Game logic integration
│   ├── database/          # Database models and operations
│   ├── models/            # Pydantic models
│   ├── services/          # Services (bot service, etc.)
│   └── utils/             # Utilities (auth, room codes)
├── frontend/              # Phase 2: React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utilities
│   └── package.json
├── main.py                # Phase 1: Interactive game
├── simulate.py            # Phase 1: Simulation system
└── requirements.txt       # Python dependencies
```
