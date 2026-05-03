# Phase 04 - Tasks - Dynamic Menu Layout Profiles

## Goal

Implement a scalable dynamic menu profile system for the fintech CMS platform.

Users should be able to select predefined menu layouts that dynamically control sidebar rendering.

The current existing sidebar/menu implementation must be preserved and used as the default:

```text id="1"
Standard Menu Profile
```

---

# Backend Tasks

## 1. Analyze Existing Sidebar Structure

* [x] identify current menu structure
* [x] identify current menu groups
* [x] identify current routes
* [x] identify icons
* [x] identify nested menus
* [x] identify ordering logic

Requirements:

* use the current menu structure as baseline
* avoid breaking current navigation

---

## 2. Create Menu Profile Models

* [x] create menu_profiles model
* [x] create menus model
* [x] create profile_menus model
* [x] create user_menu_profiles model
* [x] implement nested menu relationships
* [x] implement ordering support

Requirements:

* scalable relationships
* nested menu support
* ordering support
* use the current existing menu structure as baseline

---

## 3. Create Menu Schemas

* [x] create menu response schema
* [x] create menu profile schema
* [x] create nested menu schema
* [x] create user profile selection schema

Requirements:

* support nested menu structure
* reusable schemas
* preserve existing menu behavior

---

## 4. Create Repository Layer

* [x] create menu profile repository
* [x] create menu repository
* [x] create profile menu mapping repository
* [x] create user profile repository

Requirements:

* reusable queries
* proper filtering
* scalable structure

---

## 5. Create Service Layer

* [x] implement dynamic menu generation
* [x] implement nested menu building
* [x] implement user profile selection
* [x] implement current user menu retrieval

Requirements:

* centralized business logic
* reusable menu transformation logic

---

## 6. Create Menu APIs

* [x] implement GET /menu-profiles
* [x] implement GET /menu-profiles/{id}/menus
* [x] implement POST /menu-profiles/select
* [x] implement GET /menu/current

Requirements:

* proper validation
* proper status codes
* authenticated access only

---

## 7. Create Seed Data

* [x] create Standard profile
* [x] create Compact profile
* [x] create Operations profile
* [x] create Fraud Analyst profile
* [x] migrate current sidebar menus into Standard profile
* [x] preserve current menu ordering
* [x] preserve current routes
* [x] preserve current icons/groups

Requirements:

* reusable seed structure
* scalable menu hierarchy

---

# Frontend Tasks

## 8. Create Dynamic Sidebar Component

* [x] implement dynamic rendering
* [x] implement nested menu support
* [x] implement grouped menus
* [x] implement icons
* [x] implement active states
* [x] implement collapsible groups

Requirements:

* preserve current UX behavior
* avoid full sidebar rewrite initially
* avoid hardcoded menu structures

---

## 9. Create Menu Service

* [x] implement fetch menu profiles
* [x] implement fetch current menu
* [x] implement select menu profile

Requirements:

* reusable API layer
* clean separation

---

## 10. Create Menu Store

* [x] implement current menu profile state
* [x] implement sidebar state
* [x] implement menu loading state

Requirements:

* reusable state management
* scalable structure

---

## 11. Create Menu Profile Selector Page

* [x] implement profile list UI
* [x] implement profile preview
* [x] implement profile selection
* [x] implement loading/error handling

Requirements:

* clean UI
* responsive layout

---

## 12. Integrate Dynamic Sidebar

* [x] load menus after login
* [x] update sidebar dynamically
* [x] support profile switching without reload
* [x] preserve current Standard sidebar behavior

---

# Migration Tasks

## 13. Migrate Existing Sidebar To Standard Profile

* [x] extract current menu configuration
* [x] create Standard profile seed
* [x] map existing routes
* [x] map existing icons
* [x] map existing menu groups
* [x] map existing nested menus

Requirements:

* existing sidebar behavior remains unchanged
* existing routes continue working
* existing menus do not disappear

---

# Testing Tasks

## 14. Backend Testing

* [x] test menu retrieval
* [x] test nested menu generation
* [x] test profile selection
* [x] test API validation

---

## 15. Frontend Testing

* [x] test dynamic rendering
* [x] test nested menus
* [x] test active states
* [x] test profile switching
* [x] test sidebar updates
* [x] test Standard profile rendering

---

# Review Tasks

## 16. Review Backend Architecture

* [x] review scalability
* [x] review modularity
* [x] review reusable logic
* [x] review nested menu handling

---

## 17. Review Frontend Architecture

* [x] review reusable sidebar components
* [x] review rendering performance
* [x] review scalability
* [x] review state management

---

# Acceptance Criteria

* [x] current sidebar becomes Standard profile
* [x] existing menu behavior remains unchanged
* [x] users can select menu profiles
* [x] sidebar renders dynamically
* [x] nested menus work correctly
* [x] menu ordering works correctly
* [x] menu profile switching works correctly
* [x] sidebar updates without reload
* [x] frontend contains no hardcoded sidebar menus
* [x] architecture supports future extensibility

---

# Technical Constraints

* avoid breaking existing authentication flow
* maintain modular architecture
* support scalable future growth
* keep implementation clean and maintainable
* use the current existing menu structure as baseline

# Aditional features
* [x] define menu profile 
  * [x] profile name 
  * [x] profile status ( active/deactivate)
  * [x] button actions 
    * [x] active
    * [x] deactivate
* [x] define item page 
  * [x] suggestion Fields
    * [x] item name 
    * [x] item label
    * [x] link to component/page "jsx file" 
  * [x] define role of item
  * [x]  button actions
    * [x]  add
    * [x]  delete
    * [x]  active
    * [x]  deactivate 
* [x] user will be able to select one menu profile 
  * [x] Compact 
  * [x] Fraud Analyst
  * [x] Operations
  * [x] Standard
  * [x] Reports & Files
* [x] make Key & permission as drop down list to make it easy
* [x] add icon for menu items
* [x] group all menu item & menu profile under Menu Group
 