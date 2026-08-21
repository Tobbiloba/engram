"""
Database module - handles data persistence.
Uses SQLite for local storage with connection pooling.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

class Database:
    """SQLite database wrapper with connection management."""

    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Initialize the database schema."""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Get a database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_user(self, username: str, email: str, password_hash: str, salt: str) -> int:
        """Create a new user and return their ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, salt)
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get a user by their username."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            return dict(row) if row else None

    def get_posts_by_user(self, user_id: int) -> List[Dict]:
        """Get all posts by a user."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(row) for row in rows]
