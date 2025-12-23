"""
FastAPI backend for 4D Tic-Tac-Toe web game.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize database before importing routes
from backend.database.db import init_db
init_db()

from backend.api.routes import rooms, game

app = FastAPI(
    title="4D Tic-Tac-Toe API",
    description="Backend API for 4D Tic-Tac-Toe multiplayer game",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "4D Tic-Tac-Toe API",
        "version": "1.0.0"
    }

# Register routes
app.include_router(rooms.router, prefix="/api", tags=["rooms"])
app.include_router(game.router, prefix="/api", tags=["game"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

