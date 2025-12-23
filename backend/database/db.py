"""
Database abstraction layer for room and game persistence.
Supports SQLite (development) and PostgreSQL (production).
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import json

Base = declarative_base()


class RoomDB(Base):
    """Room database model."""
    __tablename__ = "rooms"
    
    room_code = Column(String(6), primary_key=True)
    state = Column(String(20), default="waiting")  # waiting, playing, finished
    host_player_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    winner_player_id = Column(String(36), nullable=True)
    board_state = Column(JSON, nullable=True)  # Store board state as JSON
    
    players = relationship("PlayerDB", back_populates="room", cascade="all, delete-orphan")
    moves = relationship("MoveDB", back_populates="room", cascade="all, delete-orphan")


class PlayerDB(Base):
    """Player database model."""
    __tablename__ = "players"
    
    player_id = Column(String(36), primary_key=True)
    room_code = Column(String(6), ForeignKey("rooms.room_code"), nullable=False)
    player_name = Column(String(50), nullable=False)
    symbol = Column(String(2), nullable=False)
    is_bot = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("RoomDB", back_populates="players")
    moves = relationship("MoveDB", back_populates="player")


class MoveDB(Base):
    """Move database model."""
    __tablename__ = "moves"
    
    move_id = Column(Integer, primary_key=True, autoincrement=True)
    room_code = Column(String(6), ForeignKey("rooms.room_code"), nullable=False)
    player_id = Column(String(36), ForeignKey("players.player_id"), nullable=False)
    w = Column(Integer, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    z = Column(Integer, nullable=False)
    move_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("RoomDB", back_populates="moves")
    player = relationship("PlayerDB", back_populates="moves")


# Database setup
_db_url = os.getenv("DATABASE_URL", "sqlite:///./data/game.db")
_engine = create_engine(_db_url, connect_args={"check_same_thread": False} if "sqlite" in _db_url else {})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def init_db():
    """Initialize database tables."""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=_engine)


def get_db() -> Session:
    """Get database session."""
    db = _SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller manage


# Room operations
def create_room(room_code: str, host_player_id: str) -> RoomDB:
    """Create a new room."""
    db = get_db()
    try:
        room = RoomDB(
            room_code=room_code,
            host_player_id=host_player_id,
            state="waiting",
            created_at=datetime.utcnow()
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        return room
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def get_room_by_code(room_code: str) -> Optional[RoomDB]:
    """Get room by code."""
    db = get_db()
    try:
        return db.query(RoomDB).filter(RoomDB.room_code == room_code).first()
    finally:
        db.close()


def update_room(room_code: str, **kwargs) -> bool:
    """Update room fields."""
    db = get_db()
    try:
        room = db.query(RoomDB).filter(RoomDB.room_code == room_code).first()
        if room is None:
            return False
        
        for key, value in kwargs.items():
            if hasattr(room, key):
                setattr(room, key, value)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


# Player operations
def add_player_to_room(room_code: str, player_id: str, player_name: str, symbol: str, is_bot: bool = False) -> PlayerDB:
    """Add a player to a room."""
    db = get_db()
    try:
        player = PlayerDB(
            player_id=player_id,
            room_code=room_code,
            player_name=player_name,
            symbol=symbol,
            is_bot=is_bot,
            joined_at=datetime.utcnow()
        )
        db.add(player)
        db.commit()
        db.refresh(player)
        return player
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def get_player_by_id(player_id: str) -> Optional[PlayerDB]:
    """Get player by ID."""
    db = get_db()
    try:
        return db.query(PlayerDB).filter(PlayerDB.player_id == player_id).first()
    finally:
        db.close()


def get_players_by_room(room_code: str) -> List[PlayerDB]:
    """Get all players in a room."""
    db = get_db()
    try:
        return db.query(PlayerDB).filter(PlayerDB.room_code == room_code).order_by(PlayerDB.joined_at).all()
    finally:
        db.close()


# Move operations
def save_move(room_code: str, player_id: str, w: int, x: int, y: int, z: int, move_number: int) -> MoveDB:
    """Save a move to the database."""
    db = get_db()
    try:
        move = MoveDB(
            room_code=room_code,
            player_id=player_id,
            w=w, x=x, y=y, z=z,
            move_number=move_number,
            created_at=datetime.utcnow()
        )
        db.add(move)
        db.commit()
        db.refresh(move)
        return move
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def get_moves_by_room(room_code: str) -> List[MoveDB]:
    """Get all moves for a room, ordered by move number."""
    db = get_db()
    try:
        return db.query(MoveDB).filter(MoveDB.room_code == room_code).order_by(MoveDB.move_number).all()
    finally:
        db.close()


# Database initialization should be called explicitly, not on import
# Call init_db() when starting the server

