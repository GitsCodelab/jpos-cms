import hmac
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
try:
    import bcrypt
except ImportError:
    bcrypt = None
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
	"""Hash password using bcrypt or fallback to plain text."""
	if bcrypt:
		return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
	else:
		# Fallback: simple encoding (NOT production safe)
		import base64
		return base64.b64encode(password.encode()).decode()


def verify_password(password: str, password_hash: str) -> bool:
	"""Verify password against hash using bcrypt or fallback."""
	if bcrypt:
		try:
			return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
		except Exception:
			return False
	else:
		# Fallback: simple comparison
		import base64
		try:
			return hmac.compare_digest(password, base64.b64decode(password_hash).decode())
		except Exception:
			return False


def _jwt_secret_key() -> str:
	return os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")


def _jwt_algorithm() -> str:
	return os.getenv("JWT_ALGORITHM", "HS256")


def _token_expiry_minutes() -> int:
	return int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def authenticate_user(username: str, password: str) -> bool:
	expected_username = os.getenv("AUTH_USERNAME", "admin")
	expected_password = os.getenv("AUTH_PASSWORD", "admin123")
	return hmac.compare_digest(username, expected_username) and hmac.compare_digest(password, expected_password)


def create_access_token(subject: str, role: str = "admin", jti: str | None = None) -> str:
	"""Create JWT access token with JTI (JWT ID) for revocation support."""
	if jti is None:
		jti = str(uuid.uuid4())
	
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=_token_expiry_minutes())
	payload = {
		"sub": subject,
		"role": role,
		"jti": jti,  # JWT ID for individual token revocation
		"exp": expires_at,
		"iat": datetime.now(timezone.utc),
	}
	return jwt.encode(payload, _jwt_secret_key(), algorithm=_jwt_algorithm())


def require_jwt_token(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Dict[str, Any]:
	"""Validate JWT token and check if revoked."""
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
		raise HTTPException(status_code=401, detail="Invalid or expired token")

	# Check token blacklist (if available)
	jti = payload.get("jti")
	if jti:
		# Defer blacklist check to avoid circular imports
		# This will be validated in the endpoint using the token
		payload["_jti_for_blacklist_check"] = jti

	return payload


def access_token_ttl_seconds() -> int:
	return _token_expiry_minutes() * 60
