# Phase 1 - Authentication: Action Plan

**Last Updated**: May 2, 2026  
**Status**: Ready for Implementation  
**Completion Timeline**: 20-25 hours

---

## Overview

This document provides a prioritized, actionable plan to move authentication from "working prototype" to "production-ready enterprise system."

---

## Quick Status Check

Run this to verify current state:

```bash
# Start containers
docker-compose up -d

# Test endpoints
curl http://localhost:8000/health
curl -H "Authorization: Bearer invalid" http://localhost:8000/ping  # Should be 401
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq '.access_token'
```

Expected results:
- ✅ /health returns 200
- ✅ /ping without token returns 401
- ✅ /ping with valid token returns 200
- ❌ /auth/me missing (implement in Sprint 1)
- ❌ /auth/logout missing (implement in Sprint 1)

---

## Implementation Roadmap

### Sprint 1: Critical Missing Features (2-3 days)
**Goal**: Complete Phase 1 specification requirements

- [ ] **Add `/auth/me` endpoint** (1 hour)
  - Returns: `{ username, role, expires_at }`
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.1
  - Test: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me`

- [ ] **Add `/auth/logout` endpoint** (1 hour)
  - Returns: `{ status: "ok", message: "Logged out" }`
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.1
  - Test: `curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/logout`

- [ ] **Update frontend to call new endpoints** (1 hour)
  - Update `api.js` with logout/getMe methods
  - Update App.jsx to call /auth/me on mount
  - Add proper loading/error states

- [ ] **Fix CORS configuration** (30 minutes)
  - Replace `allow_origins=["*"]` with environment-based config
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.2
  - Test in docker-compose with different origins

- [ ] **Add JTI (JWT ID) to tokens** (30 minutes)
  - Update `create_access_token()` to include jti
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.3
  - Verify tokens in jwt.io include jti field

- [ ] **Add rate limiting** (1 hour)
  - Install slowapi: `pip install slowapi`
  - Apply to /auth/login endpoint
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.4
  - Test: Spam login endpoint, should get 429 after 5 attempts

- [ ] **Add login audit logging** (2 hours)
  - Create LoginAudit model
  - Log to database on every login attempt
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 1.5
  - Query results: Check database for audit trail

**Deliverables**:
- ✅ All 3 required endpoints implemented
- ✅ Phase 1 specification fully met
- ✅ Basic security hardening in place

**Review Checklist**:
- [ ] All endpoints respond with correct status codes
- [ ] Error messages are clear and consistent
- [ ] Rate limiting works (verified with curl spam)
- [ ] Audit logs show in database
- [ ] Frontend handles new endpoints gracefully
- [ ] CORS allows frontend, blocks unauthorized origins

---

### Sprint 2: Security Hardening (3-5 days)
**Goal**: Implement enterprise-grade security practices

- [ ] **Implement token blacklist** (3 hours)
  - Add TokenBlacklist model
  - Check blacklist in `require_jwt_token()`
  - Add cleanup job for expired entries
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 2.1

- [ ] **Switch to httpOnly cookies** (4 hours)
  - Update login to set Set-Cookie header
  - Remove token from JSON response (or keep for backward compat)
  - Update frontend to remove localStorage handling
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 2.2
  - Browser DevTools: Verify cookie has httpOnly flag in Application tab

- [ ] **Add password hashing to User model** (2 hours)
  - Add bcrypt: `pip install bcrypt`
  - Create User table with password_hash field
  - Hash passwords on creation
  - Update authentication to use bcrypt.verify()
  - Migration: Hash existing default admin password

- [ ] **Implement refresh tokens** (6 hours)
  - Split access/refresh token types
  - Add /auth/refresh endpoint
  - Implement token rotation (invalidate old refresh tokens)
  - Update frontend to auto-refresh before expiry
  - Code: Create separate refresh token generation function

- [ ] **Add account lockout after failed attempts** (2 hours)
  - Track failed login attempts per user
  - Lock account after 5 failed attempts
  - Unlock after 15 minutes or manual admin action
  - Log lockout events

**Deliverables**:
- ✅ Tokens can be revoked (blacklist)
- ✅ Secure cookie storage (no XSS exposure)
- ✅ Passwords properly hashed (bcrypt)
- ✅ Session extension (refresh tokens)
- ✅ Brute force protection (account lockout)

**Security Review Checklist**:
- [ ] No tokens in localStorage
- [ ] Cookies have httpOnly, Secure, SameSite flags
- [ ] Token blacklist works (logout truly logs out)
- [ ] Refresh tokens rotate and expire
- [ ] Failed login attempts are tracked
- [ ] Passwords in database are hashed, not plain text
- [ ] No sensitive data in error messages

---

### Sprint 3: Enterprise Architecture (3-4 days)
**Goal**: Build scalable, maintainable auth system

- [ ] **Create AuthService class** (4 hours)
  - Extract business logic from routes
  - Make testable and reusable
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 3.1
  - Refactor main.py to use AuthService

- [ ] **Implement user database model** (3 hours)
  - Create User table with all fields
  - Add UserRepository for CRUD
  - Migrate from environment-based to database users
  - Add seed script for default admin user

- [ ] **Create session management** (4 hours)
  - UserSession model to track active sessions
  - List sessions endpoint
  - Revoke session endpoint (logout all others)
  - Auto-expire inactive sessions

- [ ] **Improve frontend auth state** (3 hours)
  - Create useAuth hook with Context
  - Implement ProtectedRoute component
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md section 3.2
  - Replace localStorage-based approach

- [ ] **Add comprehensive test suite** (6 hours)
  - Unit tests for security functions
  - Integration tests for auth flow
  - Test error scenarios
  - Code: See AUTH_IMPROVEMENTS_GUIDE.md Testing section

- [ ] **Create API documentation** (2 hours)
  - OpenAPI specs for all auth endpoints
  - Postman collection for auth flow
  - Usage examples and error codes
  - Update backend/API_SPECIFICATION.md

**Deliverables**:
- ✅ Scalable multi-user auth system
- ✅ Complete test coverage
- ✅ Professional API documentation
- ✅ Session management for admin control
- ✅ Enterprise-ready architecture

**Architecture Review Checklist**:
- [ ] All business logic in services, not routes
- [ ] All CRUD operations in repositories
- [ ] Dependency injection used throughout
- [ ] Tests cover happy path + errors
- [ ] API docs complete and accurate
- [ ] Session tracking working
- [ ] Code follows enterprise patterns

---

## Daily Standup Template

Use this to track progress:

```markdown
## Day X - Sprint 1

### Completed
- [ ] /auth/me endpoint
- [ ] /auth/logout endpoint

### In Progress
- [ ] Frontend integration

### Blockers
- None

### Tomorrow
- Rate limiting
```

---

## Testing Strategy

### Manual Testing (Immediate)

```bash
# Terminal 1: Start services
docker-compose up

# Terminal 2: Run tests
# Test 1: Missing endpoint
curl http://localhost:8000/auth/me  # Should be 404 before implementation

# Test 2: Login flow
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Test 3: Protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/ping

# Test 4: Rate limiting (when implemented)
for i in {1..10}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}'
done

# Should see 429 after 5 attempts
```

### Automated Testing (Sprint 3)

```bash
cd backend
pytest tests/test_security.py -v
pytest tests/test_auth_flow.py -v
pytest tests/ --cov=app --cov-report=html
```

---

## Documentation Updates Needed

| File | Changes | Priority |
|------|---------|----------|
| backend/API_SPECIFICATION.md | Add /auth/me, /auth/logout specs | High |
| backend/IMPLEMENTATION_SUMMARY.md | Update auth section | High |
| backend/.env.example | Add new env variables | Medium |
| frontend/README.md | Update auth flow docs | Medium |
| docker-compose.yml | Add env var mappings | Medium |
| CLAUDE.md | Update auth architecture | Low |

---

## Risk Mitigation

### Risk: Breaking changes to login response format

**Mitigation**:
- Keep existing response format initially
- Add new fields (expires_at, etc.)
- Communicate deprecation timeline
- Test backward compatibility

### Risk: CORS changes breaking frontend

**Mitigation**:
- Test in staging first
- Keep old CORS config for local dev
- Use environment-specific settings
- Document required origins for deployment

### Risk: Database migrations failing

**Mitigation**:
- Test migrations on staging database first
- Keep rollback scripts ready
- Run migrations in maintenance window
- Verify data integrity after migration

### Risk: Token blacklist causing performance issues

**Mitigation**:
- Add index on `jti` column
- Implement cleanup job for expired entries
- Consider Redis for large-scale deployments
- Monitor query performance

---

## Success Criteria

### Phase 1 Complete When:
- [ ] All 3 auth endpoints implemented and tested
- [ ] All Phase 1 specification requirements met
- [ ] Manual testing passes all scenarios
- [ ] CORS properly configured
- [ ] Rate limiting works
- [ ] Audit logs present

### Phase 2 Complete When:
- [ ] No tokens in localStorage
- [ ] Tokens can be revoked (blacklist)
- [ ] Passwords hashed with bcrypt
- [ ] Refresh token flow working
- [ ] Account lockout implemented
- [ ] Security team approval

### Phase 3 Complete When:
- [ ] AuthService used throughout
- [ ] User database model in place
- [ ] Session management implemented
- [ ] Test coverage >80%
- [ ] API documentation complete
- [ ] Ready for production deployment

---

## Quick Reference: Common Tasks

### Debug token content
```bash
TOKEN="your_token_here"
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq '.'
```

### Check database for audit logs
```bash
sqlite3 app.db "SELECT * FROM login_audit ORDER BY timestamp DESC LIMIT 5;"
```

### Verify environment variables
```bash
docker-compose exec jpos-cms-backend env | grep -i auth
```

### Clear data for fresh testing
```bash
docker-compose down -v  # Remove volumes
docker-compose up       # Restart clean
```

---

## Next Actions (This Week)

1. ✅ **Read** AUTH_PHASE_REVIEW.md (overview of issues)
2. ✅ **Read** AUTH_IMPROVEMENTS_GUIDE.md (code examples)
3. ⏭️ **Implement** Sprint 1 (critical missing features) - 2-3 days
4. ⏭️ **Test** Sprint 1 with manual test script
5. ⏭️ **Review** with team before Sprint 2

---

## Questions to Answer Before Starting

- [ ] Will production use HTTPS? (Required for secure cookies)
- [ ] What's the target deployment platform? (Affects CORS config)
- [ ] Should users self-register or admin-only? (Affects User model)
- [ ] Need 2FA/MFA? (Plan for later sprints)
- [ ] What's the refresh token lifetime? (7 days default, configurable)
- [ ] Who manages token blacklist cleanup? (Scheduled job or manual)

---

## Files to Review

1. **AUTH_PHASE_REVIEW.md** - Full analysis of current state
   - Implementation vs requirements comparison
   - Security concerns with detailed explanations
   - Production readiness checklist

2. **AUTH_IMPROVEMENTS_GUIDE.md** - Code examples and implementations
   - Copy-paste ready code for each fix
   - Testing recommendations
   - Deployment configuration

3. **This file** - Action plan and timeline
   - Daily tasks
   - Success criteria
   - Risk mitigation

---

## Escalation Path

If issues arise:

1. **Technical blocker**: Check DEBUG section below
2. **Design question**: Reference Phase 1 spec (phase-1-auth.md)
3. **Architecture question**: Review CLAUDE.md and enterprise patterns
4. **Security concern**: Check AUTH_PHASE_REVIEW.md security section

---

## DEBUG: Troubleshooting

### Issue: /auth/me returns 404

**Cause**: Endpoint not implemented yet

**Fix**: Add to main.py (see AUTH_IMPROVEMENTS_GUIDE.md section 1.1)

### Issue: CORS errors in browser

**Cause**: Frontend origin not in ALLOWED_ORIGINS

**Fix**: Add to environment variables or .env file

### Issue: Rate limiting not working

**Cause**: slowapi not installed

**Fix**: `pip install slowapi` and rebuild container

### Issue: Tests failing

**Cause**: Database not initialized

**Fix**: Run `docker-compose exec jpos-cms-backend python -c "from app.db import init_db; from app.db import engine, SessionLocal; init_db()"`

---

## Metrics to Track

- [ ] API response time (should be <100ms)
- [ ] Failed login attempts (track for brute force)
- [ ] Token refresh success rate (should be >99%)
- [ ] Logout completion rate (should be 100%)
- [ ] Test coverage (target: >80%)
- [ ] Security scan results (0 critical findings)

---

## Go Live Checklist

- [ ] All tests passing
- [ ] Security review completed
- [ ] Load testing done (1000+ concurrent users)
- [ ] Backup/recovery tested
- [ ] Monitoring alerts configured
- [ ] Documentation complete
- [ ] Team trained on new flows
- [ ] Rollback plan ready
- [ ] Stakeholder sign-off
