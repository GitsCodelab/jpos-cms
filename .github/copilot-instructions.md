# JPOS CMS - Copilot Instructions

## Project Overview

This project is a fintech CMS platform.

Responsibilities:

* reconciliation
* settlement monitoring
* fraud monitoring
* transaction dashboards
* operational management

Important:

* This project does NOT implement the jPOS switch itself.
* The jPOS switch exists in a separate external project.
* This CMS reads transaction and settlement data from Oracle databases populated by external systems.

---

# Tech Stack

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL (current)
* Oracle-ready architecture

## Frontend

* React
* Vite
* Axios

## Infrastructure

* Docker Compose

---

# Architecture Rules

* keep modular architecture

* avoid tightly coupled services

* prefer reusable services/components

* maintain clean separation between:

  * routers
  * services
  * repositories
  * schemas
  * models

* avoid business logic inside routers

* repositories handle database access only

* services contain business logic

* routers handle request/response only

---

# Backend Guidelines

* use async-ready patterns
* use pagination for large queries
* optimize database access
* avoid N+1 query patterns
* prefer bulk operations for reconciliation logic
* maintain Oracle compatibility
* use proper validation and error handling
* keep APIs backward compatible

---

# Frontend Guidelines

* use reusable components
* keep API logic separated
* avoid duplicated state logic
* use scalable folder structure
* support loading/error states
* support responsive layouts

---

# Security Rules

* validate all inputs
* never expose sensitive data
* use secure JWT handling
* protect authenticated endpoints
* use proper HTTP status codes
* avoid insecure token storage patterns

---

# AI Assistant Behavior

When implementing features:

1. analyze existing structure first
2. avoid breaking existing endpoints
3. explain architecture decisions
4. keep implementation modular
5. prefer scalable enterprise patterns
6. avoid unnecessary rewrites
7. explain created files before implementation

---

# Documentation Rules

* keep architecture docs inside `/docs`
* keep API specifications inside `/docs/api`
* keep phase documents inside `/docs/phases`
* keep review documents inside `/docs/reviews`

---

# Coding Style

* prefer readability
* avoid overly complex abstractions
* use descriptive naming
* keep functions focused and small
* keep business rules centralized

---

# Important Context

This is a long-term enterprise fintech platform expected to grow significantly over time.

Focus on:

* scalability
* maintainability
* clean architecture
* production readiness
* Oracle compatibility
* reconciliation performance
* fraud monitoring extensibility
