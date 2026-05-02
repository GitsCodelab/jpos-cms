# Auth Improvements Guide

Last updated: 2026-05-03

## Immediate Improvements

1. Consolidate credential verification paths
- ensure only DB-backed auth path is used in production flows
- keep env-based helper strictly for non-production fallback or remove it

2. Add protective controls
- rate limiting on login endpoint
- lockout/backoff policy after repeated failures
- structured audit events for suspicious activity

3. Strengthen tests
- login success/failure cases
- logout and token blacklist enforcement
- revoke-all-sessions behavior
- change-password invalidates all active sessions

## Short-Term Enhancements

- add role-based decorators/dependencies for admin-only endpoints
- add token lifecycle observability metrics
- document key rotation process for JWT secret

## Longer-Term Enhancements

- optional refresh-token architecture
- centralized policy management for permissions
- SIEM-compatible audit export pipeline
