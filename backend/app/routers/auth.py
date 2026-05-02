"""Authentication router - handles login, logout, and user session management."""
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserProfileResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from app.security import require_jwt_token, _token_expiry_minutes
from app.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get authenticated service for dependency injection."""
    return AuthService(db)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Login endpoint - authenticate user and return JWT token.
    
    Args:
        credentials: username and password
        
    Returns:
        LoginResponse with access_token and user info
    """
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]
    
    # Authenticate user
    user, success, failure_reason = auth_service.authenticate_user(
        credentials.username,
        credentials.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=failure_reason or "Invalid credentials")
    
    # Create session and token
    token, jti = auth_service.create_session(
        user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Calculate expiry
    expires_in = _token_expiry_minutes() * 60  # seconds
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user={
            "username": user.username,
            "role": user.role,
            "email": user.email,
        },
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserProfileResponse:
    """
    Get current authenticated user profile.
    
    Returns:
        UserProfileResponse with username, role, email, etc.
    """
    username = payload.get("sub")
    jti = payload.get("jti")
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if token is blacklisted
    if jti and auth_service.is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # Get user from database
    db = auth_service.db
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get expiry from token
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    return UserProfileResponse(
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        token_expires_at=expires_at,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """
    Logout endpoint - revoke current token and end session.
    
    Returns:
        LogoutResponse with success message
    """
    username = payload.get("sub")
    jti = payload.get("jti")
    
    if not username or not jti:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Logout user (revoke token)
    success = auth_service.logout_user(jti, username, reason="logout")
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to logout")
    
    return LogoutResponse(message="Successfully logged out")


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> ChangePasswordResponse:
    """
    Change user password.
    
    Note: Changing password revokes all existing sessions for security.
    
    Args:
        request: old_password and new_password
        
    Returns:
        ChangePasswordResponse with success message
    """
    username = payload.get("sub")
    jti = payload.get("jti")
    
    # Get user
    db = auth_service.db
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Change password
    success = auth_service.change_password(user.id, request.old_password, request.new_password)
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    return ChangePasswordResponse(
        message="Password changed successfully",
        token_revocation_message="All active sessions have been revoked for security",
    )


@router.get("/sessions", response_model=list)
async def get_active_sessions(
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get all active sessions for current user."""
    username = payload.get("sub")
    jti = payload.get("jti")
    
    if not username or not jti:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if token is blacklisted
    if auth_service.is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # Get user
    db = auth_service.db
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active sessions
    sessions = auth_service.get_active_sessions(user.id)
    
    return [
        {
            "id": s.id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
        }
        for s in sessions
    ]


@router.post("/revoke-all-sessions")
async def revoke_all_sessions(
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Revoke all active sessions (logout from all devices)."""
    username = payload.get("sub")
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user
    db = auth_service.db
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Revoke all sessions
    success = auth_service.revoke_all_sessions(user.id, reason="user_request")
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to revoke sessions")
    
    return {"message": "All sessions revoked successfully"}


@router.post("/cleanup-tokens")
async def cleanup_expired_tokens(
    payload: Dict = Depends(require_jwt_token),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    [Admin only] Clean up expired blacklist entries.
    
    This endpoint should only be accessible to admin users.
    """
    role = payload.get("role")
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    deleted = auth_service.cleanup_expired_tokens()
    
    return {
        "message": f"Cleaned up {deleted} expired tokens",
        "count": deleted,
    }


@router.get("/health")
async def auth_health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "authentication"}
