"""Authentication service - handles login, logout, token refresh, and user management."""
import uuid
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import User, UserSession, LoginAudit, TokenBlacklist
from app.security import (
    create_access_token,
    verify_password,
    hash_password,
    _token_expiry_minutes,
)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Optional[User], bool, Optional[str]]:
        """
        Authenticate user credentials.

        Returns:
            Tuple of (user, success, failure_reason)
        """
        # Find user
        user = self.db.query(User).filter(User.username == username).first()

        # Log attempt
        failure_reason = None
        success = False

        if not user:
            failure_reason = "User not found"
        elif not user.is_active:
            failure_reason = "User account is inactive"
        elif not verify_password(password, user.password_hash):
            failure_reason = "Invalid password"
        else:
            success = True

        # Create audit log
        audit = LoginAudit(
            id=str(uuid.uuid4()),
            username=username,
            user_id=user.id if user else None,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            timestamp=datetime.utcnow(),
        )
        self.db.add(audit)
        self.db.commit()

        return user if success else None, success, failure_reason

    def create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Create a new user session and return (access_token, jti).

        Args:
            user: Authenticated user
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Tuple of (access_token, jti)
        """
        # Generate JTI for token revocation tracking
        jti = str(uuid.uuid4())

        # Create access token
        token = create_access_token(user.username, user.role, jti)

        # Calculate expiry
        from datetime import timedelta, timezone

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=_token_expiry_minutes()
        )

        # Create session record
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            revoked=False,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        self.db.add(session)

        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        return token, jti

    def logout_user(self, jti: str, username: str, reason: str = "logout") -> bool:
        """
        Logout user by revoking their token.

        Args:
            jti: JWT ID to revoke
            username: Username for audit
            reason: Reason for revocation (logout, password_change, role_change, admin_revoke)

        Returns:
            True if successful
        """
        try:
            # Find session
            session = self.db.query(UserSession).filter(
                UserSession.token_jti == jti
            ).first()

            if session:
                session.revoked = True
                self.db.commit()

            # Add to blacklist
            from datetime import timedelta, timezone

            expires_at = datetime.utcnow() + timedelta(
                minutes=_token_expiry_minutes()
            )

            blacklist_entry = TokenBlacklist(
                id=str(uuid.uuid4()),
                jti=jti,
                username=username,
                reason=reason,
                token_expires_at=expires_at,
                blacklisted_at=datetime.utcnow(),
            )
            self.db.add(blacklist_entry)
            self.db.commit()

            return True
        except Exception as e:
            self.db.rollback()
            return False

    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted."""
        if not jti:
            return False

        blacklist_entry = self.db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti
        ).first()

        return blacklist_entry is not None

    def get_user_by_jti(self, jti: str) -> Optional[User]:
        """Get user by token JTI."""
        if not jti:
            return None

        session = self.db.query(UserSession).filter(
            UserSession.token_jti == jti
        ).first()

        if session and not session.revoked:
            return session.user

        return None

    def create_user(
        self, username: str, password: str, email: str, role: str = "user"
    ) -> User:
        """Create a new user."""
        # Check if user exists
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=hash_password(password),
            email=email,
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password and revoke all existing sessions."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        if not verify_password(old_password, user.password_hash):
            return False

        # Update password
        user.password_hash = hash_password(new_password)

        # Revoke all sessions
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).all()

        for session in sessions:
            session.revoked = True
            if session.token_jti:
                blacklist_entry = TokenBlacklist(
                    id=str(uuid.uuid4()),
                    jti=session.token_jti,
                    username=user.username,
                    reason="password_change",
                    token_expires_at=session.expires_at,
                    blacklisted_at=datetime.utcnow(),
                )
                self.db.add(blacklist_entry)

        self.db.commit()
        return True

    def get_active_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user."""
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.revoked == False,
        ).all()

        return sessions

    def revoke_all_sessions(self, user_id: str, reason: str = "admin_revoke") -> bool:
        """Revoke all active sessions for a user."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.revoked == False,
            ).all()

            for session in sessions:
                session.revoked = True
                if session.token_jti:
                    blacklist_entry = TokenBlacklist(
                        id=str(uuid.uuid4()),
                        jti=session.token_jti,
                        username=user.username,
                        reason=reason,
                        token_expires_at=session.expires_at,
                        blacklisted_at=datetime.utcnow(),
                    )
                    self.db.add(blacklist_entry)

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired blacklist entries. Returns count deleted."""
        try:
            deleted = self.db.query(TokenBlacklist).filter(
                TokenBlacklist.token_expires_at < datetime.utcnow()
            ).delete()
            self.db.commit()
            return deleted
        except Exception:
            self.db.rollback()
            return 0
