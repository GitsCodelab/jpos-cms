# Phase 1 - Technical Improvements: Implementation Guide

This document provides specific code examples and refactoring patterns for addressing gaps identified in the authentication review.

---

## Priority 1: Critical Security Fixes (Do First)

### 1.1 Add `/auth/logout` and `/auth/me` Endpoints

**File**: `backend/app/security.py` - Add helper function
```python
def get_current_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and validate user info from JWT payload."""
    return {
        "username": payload.get("sub"),
        "role": payload.get("role", "user"),
        "expires_at": datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc),
        "token_issued_at": datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc),
    }
```

**File**: `backend/app/main.py` - Add new endpoints
```python
@app.get("/auth/me")
def get_current_user(user_data: Dict = Depends(require_jwt_token)):
    """Get currently authenticated user info."""
    from app.security import get_current_user
    user = get_current_user(user_data)
    return {
        "username": user["username"],
        "role": user["role"],
        "expires_at": user["expires_at"].isoformat(),
    }


@app.post("/auth/logout")
def logout(user_data: Dict = Depends(require_jwt_token)):
    """
    Log out the current user.
    
    In production, should:
    1. Add token to blacklist
    2. Log the logout event
    3. Clear any sessions
    """
    username = user_data.get("sub")
    # TODO: Add to token blacklist, audit log
    return {
        "status": "ok",
        "message": f"User {username} logged out successfully",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

**Frontend Update**: `frontend/src/services/api.js`
```javascript
export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
}
```

---

### 1.2 Fix CORS for Production

**File**: `backend/app/main.py` - Replace middleware config
```python
import os

# Configure allowed origins from environment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173",  # Dev origins
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight for 1 hour
)
```

**Environment Configuration**: `backend/.env`
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Production
# ALLOWED_ORIGINS=https://cms.example.com,https://app.example.com
```

---

### 1.3 Add JTI (JWT ID) to Tokens

**File**: `backend/app/security.py` - Update token creation
```python
import uuid
from datetime import datetime, timedelta, timezone

def create_access_token(subject: str, role: str = "admin") -> str:
    """Create JWT token with unique ID (JTI) for invalidation support."""
    jti = str(uuid.uuid4())  # Unique token ID
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=_token_expiry_minutes())
    
    payload = {
        "jti": jti,  # JWT ID - unique identifier
        "sub": subject,  # Subject (username)
        "role": role,
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(expires_at.timestamp()),  # Expiration
    }
    return jwt.encode(payload, _jwt_secret_key(), algorithm=_jwt_algorithm())
```

---

### 1.4 Add Rate Limiting to Auth Endpoints

**File**: `backend/requirements.txt` - Add dependency
```
slowapi==0.1.9
```

**File**: `backend/app/main.py`
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many login attempts. Try again later."},
    )

@app.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute per IP
def login(payload: LoginRequest, request: Request):
    """Login endpoint with rate limiting."""
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token(subject=payload.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": access_token_ttl_seconds(),
        "username": payload.username,
    }
```

---

### 1.5 Implement Login Audit Logging

**File**: `backend/app/models.py` - Add audit model
```python
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean

class LoginAudit(Base):
    """Track all login attempts for security audit."""
    __tablename__ = "login_audit"
    
    id = Column(String(50), primary_key=True)
    username = Column(String(100), nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(200))  # If failed
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        return f"<LoginAudit {status} {self.username} {self.timestamp}>"
```

**File**: `backend/app/main.py` - Update login endpoint
```python
from fastapi import Request
from app.models import LoginAudit
from app.db import get_db

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Login with audit logging."""
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")[:500]
    
    # Attempt authentication
    auth_success = authenticate_user(payload.username, payload.password)
    
    # Log the attempt
    audit = LoginAudit(
        id=str(uuid.uuid4()),
        username=payload.username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=auth_success,
        failure_reason=None if auth_success else "Invalid credentials",
    )
    db.add(audit)
    db.commit()
    
    if not auth_success:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token(subject=payload.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": access_token_ttl_seconds(),
        "username": payload.username,
    }
```

---

## Priority 2: Security Hardening

### 2.1 Token Blacklist Implementation

**File**: `backend/app/models.py` - Add blacklist model
```python
class TokenBlacklist(Base):
    """Invalidated tokens (e.g., after logout or password change)."""
    __tablename__ = "token_blacklist"
    
    id = Column(String(50), primary_key=True)
    jti = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    reason = Column(String(200))  # logout, password_change, admin_revoke
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)  # When token naturally expires
```

**File**: `backend/app/security.py` - Update validation
```python
from sqlalchemy.orm import Session
from app.models import TokenBlacklist

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """Check if token has been revoked."""
    blacklist = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    return blacklist is not None

def require_jwt_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Enhanced validation including blacklist check."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required")

    try:
        payload = jwt.decode(
            credentials.credentials,
            _jwt_secret_key(),
            algorithms=[_jwt_algorithm()],
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti and is_token_blacklisted(jti, db):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    return payload
```

**File**: `backend/app/main.py` - Update logout
```python
@app.post("/auth/logout")
def logout(user_data: Dict = Depends(require_jwt_token), db: Session = Depends(get_db)):
    """Logout and blacklist token."""
    from app.models import TokenBlacklist
    import uuid
    
    username = user_data.get("sub")
    jti = user_data.get("jti")
    exp_timestamp = user_data.get("exp")
    
    if jti:
        blacklist_entry = TokenBlacklist(
            id=str(uuid.uuid4()),
            jti=jti,
            username=username,
            reason="logout",
            token_expires_at=datetime.fromtimestamp(exp_timestamp, tz=timezone.utc),
        )
        db.add(blacklist_entry)
        db.commit()
    
    return {
        "status": "ok",
        "message": "Logged out successfully",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

---

### 2.2 Implement httpOnly Cookies (Secure Token Storage)

**File**: `backend/app/main.py` - Update login to use cookies
```python
from fastapi.responses import JSONResponse

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Login and set secure httpOnly cookie.
    
    - httpOnly: Prevents JavaScript access (XSS protection)
    - Secure: Only sent over HTTPS
    - SameSite: Prevents CSRF attacks
    """
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")[:500]
    
    auth_success = authenticate_user(payload.username, payload.password)
    
    # Audit log
    audit = LoginAudit(
        id=str(uuid.uuid4()),
        username=payload.username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=auth_success,
        failure_reason=None if auth_success else "Invalid credentials",
    )
    db.add(audit)
    db.commit()
    
    if not auth_success:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create token
    token = create_access_token(subject=payload.username)
    expires_in = access_token_ttl_seconds()
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=expires_in,
        expires=expires_in,
        path="/",
        domain=None,
        secure=os.getenv("ENVIRONMENT", "development") == "production",  # HTTPS only in prod
        httponly=True,  # Prevents JavaScript access
        samesite="strict",  # CSRF protection
    )
    
    # Also return in JSON for backward compatibility (temporary)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "username": payload.username,
    }


@app.post("/auth/logout")
def logout(user_data: Dict = Depends(require_jwt_token), response: Response):
    """Logout and clear secure cookie."""
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=None,
    )
    
    return {
        "status": "ok",
        "message": "Logged out successfully",
    }
```

**Frontend Update**: `frontend/src/services/api.js` - Remove token handling
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,  // Include cookies in requests
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      // Cookie was cleared by server, trigger logout
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  },
)

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
}

export default api
```

---

## Priority 3: Enterprise Architecture

### 3.1 Create Auth Service Layer

**File**: `backend/app/services/auth_service.py` (new file)
```python
"""Authentication business logic service."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import LoginAudit, TokenBlacklist, User
from app.repositories.base_repository import BaseRepository
from app.security import authenticate_user, create_access_token


class AuthService:
    """Handles all authentication operations."""
    
    def __init__(self):
        self.user_repo = BaseRepository(User)
        self.audit_repo = BaseRepository(LoginAudit)
        self.blacklist_repo = BaseRepository(TokenBlacklist)
    
    def login(
        self,
        db: Session,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str,
    ) -> dict:
        """
        Authenticate user and return token.
        
        Logs both successful and failed attempts.
        """
        success = authenticate_user(username, password)
        
        # Always log the attempt
        audit = LoginAudit(
            id=str(uuid.uuid4()),
            username=username,
            ip_address=ip_address,
            user_agent=user_agent[:500],
            success=success,
            failure_reason=None if success else "Invalid credentials",
        )
        db.add(audit)
        db.commit()
        
        if not success:
            return {"error": "Invalid credentials", "success": False}
        
        # Create token
        token = create_access_token(subject=username)
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "username": username,
        }
    
    def logout(self, db: Session, jti: str, username: str, reason: str = "logout"):
        """Invalidate token by adding to blacklist."""
        blacklist = TokenBlacklist(
            id=str(uuid.uuid4()),
            jti=jti,
            username=username,
            reason=reason,
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(blacklist)
        db.commit()
        return {"status": "ok"}
    
    def is_token_valid(self, db: Session, jti: str) -> bool:
        """Check if token is still valid (not blacklisted)."""
        return not db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    
    def get_recent_logins(
        self,
        db: Session,
        username: str,
        limit: int = 10,
    ) -> list:
        """Get recent login attempts for user."""
        return (
            db.query(LoginAudit)
            .filter(LoginAudit.username == username)
            .order_by(LoginAudit.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    def get_login_summary(self, db: Session, hours: int = 24) -> dict:
        """Get login statistics for monitoring."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        total_attempts = db.query(LoginAudit).filter(
            LoginAudit.timestamp >= since
        ).count()
        
        successful = db.query(LoginAudit).filter(
            LoginAudit.timestamp >= since,
            LoginAudit.success == True,
        ).count()
        
        failed = total_attempts - successful
        
        return {
            "period_hours": hours,
            "total_attempts": total_attempts,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_attempts * 100) if total_attempts > 0 else 0,
        }
```

**File**: `backend/app/main.py` - Use service
```python
from app.services.auth_service import AuthService

auth_service = AuthService()

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Login using AuthService."""
    result = auth_service.login(
        db=db,
        username=payload.username,
        password=payload.password,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")[:500],
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error"))
    
    token = result.get("access_token")
    expires_in = result.get("expires_in")
    
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=expires_in,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    
    return {k: v for k, v in result.items() if k != "access_token"}
```

---

### 3.2 Improve Frontend Auth State Management

**File**: `frontend/src/hooks/useAuth.js` (new file)
```javascript
import { useContext, useEffect, useState } from 'react'
import api from '../services/api'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    setLoading(true)
    try {
      const res = await api.get('/auth/me')
      setUser(res.data)
      setError(null)
    } catch (err) {
      setUser(null)
      if (err.response?.status !== 401) {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    setLoading(true)
    try {
      const res = await api.post('/auth/login', { username, password })
      setUser({ username: res.data.username })
      setError(null)
      return true
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
      return false
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
      setUser(null)
      setError(null)
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    logout,
    checkAuth,
  }
}
```

**File**: `frontend/src/components/ProtectedRoute.jsx` (new file)
```javascript
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
```

---

## Testing Recommendations

### Unit Tests

**File**: `backend/tests/test_security.py` (new file)
```python
import pytest
from app.security import create_access_token, authenticate_user, require_jwt_token


def test_authenticate_user():
    """Test password validation."""
    assert authenticate_user("admin", "admin123") == True
    assert authenticate_user("admin", "wrong") == False


def test_create_access_token():
    """Test token generation."""
    token = create_access_token("testuser")
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50


def test_token_contains_jti():
    """Test JWT includes unique ID."""
    import jwt
    token = create_access_token("testuser")
    payload = jwt.decode(token, options={"verify_signature": False})
    assert "jti" in payload
    assert "iat" in payload
    assert "exp" in payload
```

### Integration Tests

**File**: `backend/tests/test_auth_flow.py` (new file)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_success():
    """Test successful login."""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    """Test failed login."""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """Test protected endpoint rejects unauthenticated request."""
    response = client.get("/ping")
    assert response.status_code == 401


def test_protected_endpoint_with_token():
    """Test protected endpoint with valid token."""
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    response = client.get("/ping", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
```

---

## Deployment Configuration

### Environment Variables

**File**: `backend/.env.example`
```bash
# Server
ENVIRONMENT=production
API_TITLE=jPOS CMS API
API_VERSION=1.0.0

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Authentication
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password

# Database
DATABASE_URL=postgresql://user:pass@localhost/jpos_cms

# CORS
ALLOWED_ORIGINS=https://cms.example.com,https://app.example.com

# Security
SECURE_COOKIES=true
HTTPS_ONLY=true
```

### Docker Compose Update

**File**: `docker-compose.yml` - Add environment variables
```yaml
services:
  jpos-cms-backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: jpos-cms-backend
    environment:
      ENVIRONMENT: ${ENVIRONMENT:-development}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-dev-secret}
      JWT_ALGORITHM: HS256
      JWT_ACCESS_TOKEN_EXPIRE_MINUTES: 60
      AUTH_USERNAME: ${AUTH_USERNAME:-admin}
      AUTH_PASSWORD: ${AUTH_PASSWORD:-admin123}
      DATABASE_URL: ${DATABASE_URL:-postgresql://postgres:postgres@localhost/jpos_cms}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-http://localhost:3000,http://localhost:5173}
    ports:
      - "8002:8000"
    networks:
      - jpos-cms-net
```

---

## Summary of Changes

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Add /auth/me and /auth/logout | 1h | High - Required endpoints |
| 1 | Fix CORS | 30m | High - Security |
| 1 | Add JTI to tokens | 30m | Medium - Required for blacklist |
| 1 | Rate limiting | 1h | High - Security |
| 1 | Login audit logging | 2h | Medium - Compliance |
| 2 | Token blacklist | 3h | High - Security |
| 2 | httpOnly cookies | 3h | High - Security |
| 3 | AuthService layer | 4h | Medium - Architecture |
| 3 | Frontend auth hooks | 2h | Medium - UX |
| 3 | Protected route component | 1h | Medium - UX |

**Total estimated effort**: 20-25 hours to full enterprise-ready implementation.

All changes can be implemented incrementally without breaking existing functionality.
