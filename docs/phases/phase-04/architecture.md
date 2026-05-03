# Phase 04
- Tasks - Dynamic Menu Layout Profiles

## Goal

Implement a scalable dynamic menu profile system for the fintech CMS platform.

Users should be able to select predefined menu layouts that dynamically control sidebar rendering.

---

# Backend Tasks

## 1. Create Menu Profile Models

Create models:

* menu_profiles
* menus
* profile_menus
* user_menu_profiles

Requirements:

* scalable relationships
* nested menu support
* ordering support
* use the current existing menu structure as baseline

---

## 2. Create Menu Schemas

Create:

* menu response schema
* menu profile schema
* nested menu schema
* user profile selection schema
* use the current existing menu structure as baseline

Requirements:

* support nested menu structure
* reusable schemas

---

## 3. Create Repository Layer

Implement repositories for:

* menu profiles
* menus
* profile menu mapping
* user profile selection
* use the current existing menu structure as baseline

Requirements:

* reusable queries
* proper filtering
* scalable structure

---

## 4. Create Service Layer

Implement services for:

* dynamic menu generation
* nested menu building
* user profile selection
* current user menu retrieval

Requirements:

* centralized business logic
* reusable menu transformation logic

---

## 5. Create Menu APIs

Implement APIs:

* GET /menu-profiles
* GET /menu-profiles/{id}/menus
* POST /menu-profiles/select
* GET /menu/current

Requirements:

* proper validation
* proper status codes
* authenticated access only

---

## 6. Create Seed Data

Create default profiles:

* Standard
* Compact
* Operations
* Fraud Analyst

Create sample menus.

Requirements:

* reusable seed structure
* scalable menu hierarchy

---

# Frontend Tasks

## 7. Create Dynamic Sidebar Component

Requirements:

* dynamic rendering
* nested menu support
* grouped menus
* icons
* active states
* collapsible groups

Avoid hardcoded menu structures.

---

## 8. Create Menu Service

Implement:

* fetch menu profiles
* fetch current menu
* select menu profile

Requirements:

* reusable API layer
* clean separation

---

## 9. Create Menu Store

Implement:

* current menu profile state
* sidebar state
* menu loading state

Requirements:

* reusable state management
* scalable structure

---

## 10. Create Menu Profile Selector Page

Allow users to:

* view profiles
* preview profiles
* select profile

Requirements:

* clean UI
* responsive layout
* loading/error handling

---

## 11. Integrate Dynamic Sidebar

Requirements:

* load menus after login
* update sidebar dynamically
* support profile switching without reload

---

# Testing Tasks

## 12. Backend Testing

Test:

* menu retrieval
* nested menu generation
* profile selection
* API validation

---

## 13. Frontend Testing

Test:

* dynamic rendering
* nested menus
* active states
* profile switching
* sidebar updates

---

# Review Tasks

## 14. Review Backend Architecture

Review:

* scalability
* modularity
* reusable logic
* nested menu handling

---

## 15. Review Frontend Architecture

Review:

* reusable sidebar components
* rendering performance
* scalability
* state management

---

# Acceptance Criteria

* users can select menu profiles
* sidebar renders dynamically
* nested menus work correctly
* menu ordering works correctly
* menu profile switching works correctly
* sidebar updates without reload
* frontend contains no hardcoded sidebar menus
* architecture supports future extensibility

---

# Technical Constraints

* avoid breaking existing authentication flow
* maintain modular architecture
* support scalable future growth
* keep implementation clean and maintainable
