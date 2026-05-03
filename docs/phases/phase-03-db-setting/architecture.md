# Phase 03 - Database Connections Management

## Goal

Implement a simple and scalable database connection management module inside the fintech CMS platform.

The module will allow administrators to:

* create database connections
* edit database connections
* delete database connections
* activate/deactivate connections
* test database connectivity

These connections will later be used by:

* reconciliation services
* reporting services
* transaction queries
* fraud monitoring services

---

# Features

## Database Connections List

Display:

* connection name
* database type
* host
* port
* database/service name
* username
* status
* active flag

Support:

* pagination
* search
* filtering

---

# Create Connection

Allow creating new database connections.

Supported database types:

* Oracle
* PostgreSQL

Fields:

* connection name
* database type
* host
* port
* service/database name
* username
* password
* schema
* description
* active flag

---

# Edit Connection

Allow updating:

* connection settings
* credentials
* active status
* connection description

---

# Delete Connection

Allow deleting unused connections safely.

Requirements:

* confirmation before delete
* avoid deleting active production connection accidentally

---

# Connection Testing

Provide:

* test connection button
* connection success/failure feedback
* validation messages

---

# Backend Requirements

## Technology

* FastAPI
* SQLAlchemy
* PostgreSQL

## Requirements

* encrypted password storage
* reusable database connection service
* proper validation
* proper error handling
* secure credential handling
* scalable repository/service architecture
* PostgreSQL-based authentication database

---

# Frontend Requirements

## Technology

* React
* Vite
* Axios

## Requirements

* clean admin UI
* reusable forms
* validation messages
* loading indicators
* success/error feedback

---

# Security Requirements

* passwords must NOT be exposed in APIs
* secure credential storage
* avoid logging credentials
* restrict access to admin users only

---

# Expected Usage

These connections will later be used for:

* Oracle SmartVista access
* reconciliation queries
* reporting queries
* fraud monitoring queries
* operational dashboards

---

# Database Configuration Requirements

## Primary Application Database

Replace SQLite with PostgreSQL.

Requirements:

* remove SQLite dependency
* migrate authentication database to PostgreSQL
* use localhost PostgreSQL instance
* create dedicated authentication database

Database Name:

```text
jpos-cms-auth
```

---

# PostgreSQL Requirements

Use local PostgreSQL instance for:

* authentication
* CMS configuration storage
* database connections management
* future CMS metadata

---

# Oracle Requirements

Oracle databases will be connected dynamically using the database connections module.

Requirements:

* support Oracle connection testing
* support Oracle connection management
* support future Oracle query integrations

---

# Non Goals

This phase does NOT include:

* reconciliation implementation
* reporting implementation
* ETL implementation
* multi-tenant routing
* database synchronization

---

# AI Tasks

Tasks:

1. design database connection model
2. design backend CRUD APIs
3. design frontend management page
4. recommend secure credential handling
5. recommend scalable connection testing approach
6. migrate SQLite authentication database to PostgreSQL
7. configure PostgreSQL environment setup
8. recommend future extensibility improvements

---

# Technical Constraints

* avoid breaking existing APIs
* maintain modular architecture
* support future scalability
* keep implementation simple and maintainable

---

# Important Notes

* Replace SQLite with PostgreSQL.
* Use localhost PostgreSQL instance.
* Create PostgreSQL database named:

```text
jpos-cms-auth
```

* Keep Oracle integrations dynamic and configurable.
* Avoid hardcoded database connection logic.
