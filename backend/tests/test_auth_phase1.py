"""Integration tests for Phase 1 authentication system."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db import engine, Base
from app.models import User, UserSession, LoginAudit, TokenBlacklist
from app.security import hash_password, verify_password, _token_expiry_minutes
from app.services.auth import AuthService


# Test database setup
@pytest.fixture
def test_db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    # Create test admin user
    admin = User(
        id="test-admin",
        username="testadmin",
        password_hash=hash_password("testadmin123"),
        email="admin@test.local",
        role="admin",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(admin)
    db.commit()
    
    yield db
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestLoginEndpoint:
    """Test /auth/login endpoint."""
    
    def test_login_success(self, client, test_db):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["username"] == "testadmin"
    
    def test_login_invalid_username(self, client, test_db):
        """Test login with invalid username."""
        response = client.post(
            "/api/auth/login",
            json={"username": "invalid", "password": "password"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_invalid_password(self, client, test_db):
        """Test login with invalid password."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpassword"},
        )
        assert response.status_code == 401
    
    def test_login_audit_logged(self, client, test_db):
        """Test that login attempts are audited."""
        client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        
        audit = test_db.query(LoginAudit).filter(
            LoginAudit.username == "testadmin"
        ).first()
        
        assert audit is not None
        assert audit.success == True


class TestAuthEndpoints:
    """Test /auth/me, /auth/logout, etc."""
    
    def test_get_current_user(self, client, test_db):
        """Test GET /auth/me endpoint."""
        # Login first
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testadmin"
        assert data["role"] == "admin"
        assert data["is_active"] == True
    
    def test_get_current_user_without_token(self, client, test_db):
        """Test GET /auth/me without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_logout(self, client, test_db):
        """Test POST /auth/logout endpoint."""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
        
        # Try to use token after logout
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should be rejected (token in blacklist)
        assert response.status_code == 401
    
    def test_change_password(self, client, test_db):
        """Test POST /auth/change-password endpoint."""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        token = login_response.json()["access_token"]
        
        # Change password
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": "testadmin123", "new_password": "newpassword123"},
        )
        assert response.status_code == 200
        
        # Try login with old password (should fail)
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testadmin123"},
        )
        assert response.status_code == 401
        
        # Try login with new password (should succeed)
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "newpassword123"},
        )
        assert response.status_code == 200


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_and_verify(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Hash should be different from plain text
        assert hashed != password
        
        # Verify should work
        assert verify_password(password, hashed) == True
        
        # Wrong password should fail
        assert verify_password("wrongpassword", hashed) == False


class TestAuthService:
    """Test AuthService class."""
    
    def test_authenticate_user_success(self, test_db):
        """Test authenticate_user with correct credentials."""
        service = AuthService(test_db)
        user, success, reason = service.authenticate_user("testadmin", "testadmin123")
        
        assert success == True
        assert user is not None
        assert user.username == "testadmin"
    
    def test_authenticate_user_failure(self, test_db):
        """Test authenticate_user with wrong credentials."""
        service = AuthService(test_db)
        user, success, reason = service.authenticate_user("testadmin", "wrongpassword")
        
        assert success == False
        assert reason == "Invalid password"
    
    def test_create_session(self, test_db):
        """Test create_session method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        token, jti = service.create_session(user)
        
        assert token is not None
        assert jti is not None
        
        # Verify session was created
        session = test_db.query(UserSession).filter(
            UserSession.token_jti == jti
        ).first()
        assert session is not None
        assert session.user_id == user.id
    
    def test_logout_user(self, test_db):
        """Test logout_user method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        # Create session
        token, jti = service.create_session(user)
        
        # Logout
        success = service.logout_user(jti, "testadmin")
        assert success == True
        
        # Verify token is blacklisted
        assert service.is_token_blacklisted(jti) == True
    
    def test_change_password(self, test_db):
        """Test change_password method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        success = service.change_password(user.id, "testadmin123", "newpassword123")
        assert success == True
        
        # Verify old password no longer works
        _, auth_success, _ = service.authenticate_user("testadmin", "testadmin123")
        assert auth_success == False
        
        # Verify new password works
        _, auth_success, _ = service.authenticate_user("testadmin", "newpassword123")
        assert auth_success == True


class TestTokenBlacklist:
    """Test token blacklist functionality."""
    
    def test_token_blacklist_on_logout(self, test_db):
        """Test that tokens are blacklisted on logout."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        # Create session
        token, jti = service.create_session(user)
        
        # Logout
        service.logout_user(jti, "testadmin")
        
        # Check blacklist
        blacklist_entry = test_db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti
        ).first()
        
        assert blacklist_entry is not None
        assert blacklist_entry.reason == "logout"
    
    def test_cleanup_expired_tokens(self, test_db):
        """Test cleanup_expired_tokens method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        # Create and logout a session
        token, jti = service.create_session(user)
        service.logout_user(jti, "testadmin")
        
        # Manually set expiry to past
        blacklist_entry = test_db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti
        ).first()
        blacklist_entry.token_expires_at = datetime.utcnow() - timedelta(hours=1)
        test_db.commit()
        
        # Cleanup
        deleted = service.cleanup_expired_tokens()
        assert deleted == 1


class TestSessionManagement:
    """Test session management features."""
    
    def test_get_active_sessions(self, test_db):
        """Test get_active_sessions method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        # Create two sessions
        token1, jti1 = service.create_session(user)
        token2, jti2 = service.create_session(user)
        
        # Get active sessions
        sessions = service.get_active_sessions(user.id)
        assert len(sessions) == 2
    
    def test_revoke_all_sessions(self, test_db):
        """Test revoke_all_sessions method."""
        service = AuthService(test_db)
        user = test_db.query(User).filter(User.username == "testadmin").first()
        
        # Create two sessions
        token1, jti1 = service.create_session(user)
        token2, jti2 = service.create_session(user)
        
        # Revoke all
        success = service.revoke_all_sessions(user.id)
        assert success == True
        
        # Verify all are blacklisted
        assert service.is_token_blacklisted(jti1) == True
        assert service.is_token_blacklisted(jti2) == True
