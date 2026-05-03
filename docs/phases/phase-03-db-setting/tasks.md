# Tasks - Database Connections Management

## Goal

Implement a simple database connections management module for the fintech CMS platform.

The module will manage database connections used later for:

-[x] Oracle SmartVista access
-[x] reconciliation services
-[x] reporting services
-[x] fraud monitoring
-[x] operational dashboards

The platform must also migrate from SQLite to PostgreSQL for core CMS/authentication storage.

---

# PostgreSQL Migration Tasks

## 1. Remove SQLite Dependency

Tasks:

-[x] remove SQLite configuration
-[x] remove SQLite database usage
-[x] remove SQLite connection logic
-[x] update environment configuration

Requirements:

-[x] keep project structure clean
-[x] avoid breaking existing APIs

---

## 2. Configure PostgreSQL

Use localhost PostgreSQL instance.

Create database:

```text id="1"
jpos-cms-auth
```

Tasks:

-[x] configure PostgreSQL connection
-[x] configure SQLAlchemy PostgreSQL engine
-[x] configure environment variables
-[x] configure database session management

Requirements:

-[x] scalable configuration
-[x] reusable connection handling
-[x] production-ready structure

---

## 3. Configure Environment Variables

Add:

-[x] PostgreSQL host
-[x] PostgreSQL port
-[x] PostgreSQL database
-[x] PostgreSQL username
-[x] PostgreSQL password

Requirements:

-[x] use .env configuration
-[x] avoid hardcoded credentials

---

# Backend Tasks

## 4. Create Database Connection Model

Create database connection entity/model with fields:

-[x] id
-[x] connection_name
-[x] database_type
-[x] host
-[x] port
-[x] service_name
-[x] username
-[x] encrypted_password
-[x] schema_name
-[x] description
-[x] is_active
-[x] created_at
-[x] updated_at

Requirements:

-[x] support Oracle and PostgreSQL
-[x] secure password handling
-[x] scalable structure

---

## 5. Create Database Connection Schemas

Create:

-[x] create schema
-[x] update schema
-[x] response schema
-[x] connection test response schema

Requirements:

-[x] validation support
-[x] secure response handling
-[x] avoid exposing passwords

---

## 6. Create Repository Layer

Create reusable repository for:

-[x] create connection
-[x] update connection
-[x] delete connection
-[x] get single connection
-[x] list connections
-[x] activate/deactivate connection

Requirements:

-[x] reusable queries
-[x] pagination support
-[x] filtering support

---

## 7. Create Service Layer

Create reusable service logic for:

-[x] validation
-[x] credential handling
-[x] connection testing
-[x] active connection management

Requirements:

-[x] centralized business logic
-[x] proper error handling
-[x] reusable architecture

---

## 8. Create Connection Test Service

Implement:

-[x] Oracle connectivity test
-[x] PostgreSQL connectivity test

Requirements:

-[x] timeout handling
-[x] validation messages
-[x] safe error responses
-[x] avoid exposing sensitive errors

---

## 9. Create API Endpoints

Create APIs:

-[x] GET /database-connections
-[x] GET /database-connections/{id}
-[x] POST /database-connections
-[x] PUT /database-connections/{id}
-[x] DELETE /database-connections/{id}
-[x] POST /database-connections/{id}/test
-[x] POST /database-connections/{id}/activate

Requirements:

-[x] pagination
-[x] filtering
-[x] validation
-[x] proper status codes

---

# Frontend Tasks

## 10. Create Database Connections Page

Create page displaying:

-[x] connection name
-[x] database type
-[x] host
-[x] status
-[x] active state

Requirements:

-[x] pagination
-[x] search
-[x] loading states
-[x] error handling

---

## 11. Create Add/Edit Connection Form

Fields:

-[x] connection name
-[x] database type
-[x] host
-[x] port
-[x] service/database name
-[x] username
-[x] password
-[x] schema
-[x] description
-[x] active flag

Requirements:

-[x] reusable form
-[x] validation
-[x] loading indicators
-[x] success/error messages

---

## 12. Create Delete Flow

Requirements:

-[x] confirmation dialog
-[x] proper warnings
-[x] success/error feedback

---

## 13. Create Connection Test UI

Requirements:

-[x] test connection button
-[x] success/failure feedback
-[x] loading indicators
-[x] validation messages

---

# Security Tasks

## 14. Secure Credential Handling

Requirements:

-[x] never expose passwords in API responses
-[x] encrypt stored passwords
-[x] avoid frontend credential leaks
-[x] avoid logging credentials

---

# Review Tasks

## 15. Review Backend Architecture

Review:

-[x] modularity
-[x] scalability
-[x] repository separation
-[x] service separation
-[x] PostgreSQL integration
-[x] error handling

---

## 16. Review Frontend Architecture

Review:

-[x] reusable components
-[x] scalable structure
-[x] API separation
-[x] loading/error handling

---

# Testing Tasks

## 17. Backend Testing

Test:

-[x] PostgreSQL connectivity
-[x] CRUD operations
-[x] Oracle connection testing
-[x] PostgreSQL connection testing
-[x] validation handling
-[x] API responses

---

## 18. Frontend Testing

Test:

-[x] create connection
-[x] edit connection
-[x] delete connection
-[x] test connection
-[x] loading/error states

---

# Acceptance Criteria

-[x] SQLite is fully removed
-[x] PostgreSQL is configured successfully
-[x] PostgreSQL database `jpos-cms-auth` is used successfully
-[x] admin can create database connection
-[x] admin can edit database connection
-[x] admin can delete database connection
-[x] admin can test database connectivity
-[x] passwords are stored securely
-[x] passwords are never exposed in APIs
-[x] Oracle connections work
-[x] PostgreSQL connections work
-[x] active connection can be selected
-[x] UI handles validation/errors correctly

---

# Technical Constraints

-[x] avoid breaking existing APIs
-[x] maintain modular architecture
-[x] support future scalability
-[x] keep implementation simple and maintainable

# Connection Rule
- [x] make only one connection "active"
- [x] if user activate a connection other should be inactive
- [x] all business APIs existing or new will use the active connection 