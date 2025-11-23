import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Request, HTTPException
from config import SESSION_LIFETIME

# In-memory session storage
sessions: Dict[str, dict] = {}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

def create_session(user_id: int, user_type: str, user_data: dict) -> str:
    """Create a new session for a user"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'user_id': user_id,
        'user_type': user_type,
        'user_data': user_data,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(seconds=SESSION_LIFETIME)
    }
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """Get session data if valid"""
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    
    # Check if session expired
    if datetime.now() > session['expires_at']:
        del sessions[session_id]
        return None
    
    # Refresh session expiry
    session['expires_at'] = datetime.now() + timedelta(seconds=SESSION_LIFETIME)
    return session

def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]

def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from request"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        return None
    
    session = get_session(session_id)
    if not session:
        return None
    
    return session['user_data']

def require_auth(request: Request, allowed_types: list = None) -> dict:
    """Require authentication with specific user types"""
    user = get_current_user(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if allowed_types and user.get('user_type') not in allowed_types:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return user

def require_admin(request: Request) -> dict:
    """Require admin authentication"""
    session_id = request.cookies.get('admin_session_id')
    if not session_id:
        raise HTTPException(status_code=401, detail="Admin not authenticated")
    
    session = get_session(session_id)
    if not session or session['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return session['user_data']

def cleanup_expired_sessions():
    """Remove expired sessions"""
    now = datetime.now()
    expired = [sid for sid, session in sessions.items() if now > session['expires_at']]
    for sid in expired:
        del sessions[sid]