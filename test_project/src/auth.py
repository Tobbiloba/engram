"""
Authentication module for the test application.
Handles user login, logout, and session management.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class SessionManager:
    """Manages user sessions with token-based authentication."""

    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=token_expiry_hours)
        self.sessions: Dict[str, dict] = {}

    def create_session(self, user_id: str) -> str:
        """Create a new session for a user and return the token."""
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + self.token_expiry
        }
        return token

    def validate_token(self, token: str) -> Optional[str]:
        """Validate a session token and return the user_id if valid."""
        session = self.sessions.get(token)
        if not session:
            return None
        if datetime.now() > session["expires_at"]:
            del self.sessions[token]
            return None
        return session["user_id"]

    def logout(self, token: str) -> bool:
        """Invalidate a session token."""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

def hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against a hash."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed
