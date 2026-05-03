# Phase 04 — Dynamic Menu Layout Profiles

## Overview

This phase introduces a **dynamic menu profile system** that allows users to select predefined sidebar layouts. The existing sidebar is preserved as the default **Standard** profile; no hardcoded menus exist in the frontend anymore.

---

## Concepts

| Concept | Description |
|---|---|
| **Menu Item** | A single navigation entry (link, group, or page) with a key, label, icon, permission, and optional parent |
| **Menu Profile** | A named collection of top-level menu items (e.g. Standard, Compact, Fraud Analyst) |
| **Profile Assignment** | The mapping between a profile and the top-level items it includes |
| **User Profile Selection** | Each user can choose which profile controls their sidebar |

---

## Available Profiles (Seed Data)

| Profile | Description |
|---|---|
| **Standard** | Full sidebar — mirrors the original hardcoded menu |
| **Compact** | Reduced item set for everyday use |
| **Operations** | Focused on operational tasks (reconciliation, settlement, routing) |
| **Fraud Analyst** | Fraud monitoring and prevention focused |
| **Reports & Files** | Reporting and file management focused |

---

## How to Use

### Selecting a Menu Profile (End User)

1. Go to **Configuration → Menu Profiles** in the sidebar.
2. The page lists all active profiles as cards.
3. Click **Select** on any profile card.
4. The sidebar immediately updates to reflect the chosen profile — no page reload required.
5. Your selection is persisted; it will be restored on next login.

---

### Managing Menu Profiles (Admin)

#### Activating / Deactivating a Profile

1. Open **Configuration → Menu Profiles**.
2. Each card shows the current status (Active / Inactive) as a tag.
3. Click **Deactivate** to hide a profile from users (cannot deactivate the default profile).
4. Click **Activate** to restore it.

#### Assigning Items to a Profile

1. Open **Configuration → Menu Profiles**.
2. Click **Manage Items** on a profile card.
3. A drawer opens with two panels:
   - **Available** — all top-level menu items not yet assigned to this profile.
   - **Assigned** — items currently included in this profile's sidebar.
4. Use the arrow buttons to move items between panels. Changes are applied immediately via the API.
5. Use the search box inside either panel to filter by label or key.
6. Close the drawer when done.

---

### Managing Menu Items (Admin)

1. Open **Configuration → Menu Items**.
2. The table shows all 119 items as an expandable tree (parent → children).
3. Use **Add Item** to create a new item. Fields:
   - **Key** — unique identifier / route path (autocomplete from existing keys)
   - **Label** — display text shown in the sidebar
   - **Icon** — searchable icon picker (55 available icons)
   - **Permission** — access control string (combobox with existing permissions)
   - **Order** — numeric sort order within its parent group
   - **Is Group** — toggle if this item is a collapsible group header (no direct route)
4. Use **Activate / Deactivate** per row to show or hide an item across all profiles.
5. Use **Delete** to permanently remove an item (only if it has no children).

---

## API Reference

### Profile Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/menu-profiles` | List all active profiles |
| `GET` | `/menu-profiles/admin/all` | List ALL profiles including inactive (admin) |
| `GET` | `/menu-profiles/{id}/menus` | Get a profile with its full nested menu tree |
| `POST` | `/menu-profiles/select` | Set the current user's profile |
| `PATCH` | `/menu-profiles/{id}/activate` | Activate a profile |
| `PATCH` | `/menu-profiles/{id}/deactivate` | Deactivate a profile |
| `GET` | `/menu-profiles/{id}/items` | List top-level item IDs assigned to a profile |
| `POST` | `/menu-profiles/{id}/items` | Assign a top-level item to a profile |
| `DELETE` | `/menu-profiles/{id}/items/{item_id}` | Remove an item from a profile |

### Menu Item Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/menu-items` | List all menu items (flat, all levels) |
| `POST` | `/menu-items` | Create a new menu item |
| `DELETE` | `/menu-items/{id}` | Delete a menu item |
| `PATCH` | `/menu-items/{id}/activate` | Activate a menu item |
| `PATCH` | `/menu-items/{id}/deactivate` | Deactivate a menu item |

### Current User Menu

| Method | Path | Description |
|---|---|---|
| `GET` | `/menu/current` | Get the resolved nested menu tree for the current user |

All endpoints require a valid JWT (`Authorization: Bearer <token>`).

---

## Architecture

```
frontend (React)
  └── MenuContext (store)         — holds current menu tree, triggers sidebar re-render
  └── pages/MenuProfiles.jsx     — profile cards + Manage Items drawer
  └── pages/MenuItems.jsx        — menu item tree table + add/delete/toggle
  └── services/menuApi.js        — all API calls for profiles and items

backend (FastAPI)
  └── routers/menu.py            — all menu endpoints
  └── services/menu_service.py   — business logic (tree building, profile resolution)
  └── repositories/
        menu_profile_repository.py   — profile CRUD + item assignment queries
        menu_item_repository.py      — item CRUD
        user_menu_profile_repository.py — user ↔ profile mapping
  └── models.py                  — MenuItem, MenuProfile, ProfileMenuItem, UserMenuProfile
  └── seed/menu_seed.py          — idempotent seed (runs on startup)
```

### Key Rules

- The sidebar is built entirely from the database — no hardcoded items in the frontend.
- `menu_seed.py` runs on every startup and is fully idempotent; re-running it does not duplicate data.
- Top-level items (`parent_id = NULL`) are the units assigned to profiles. Their full subtrees are included automatically when a profile is rendered.
- A user who has never selected a profile gets the **default** profile (marked `is_default = true` in the DB).

---

## Database Tables

| Table | Purpose |
|---|---|
| `menu_items` | All navigation entries (flat, linked by `parent_id`) |
| `menu_profiles` | Named profiles (Standard, Compact, …) |
| `profile_menu_items` | M2M: which top-level items belong to which profile |
| `user_menu_profiles` | Each user's currently selected profile |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Sidebar is empty after login | No default profile set | Ensure one profile has `is_default = true` in DB or restart backend (seed re-runs) |
| Select button returns 500 | JWT `sub` is username, not UUID | Fixed — `_resolve_user_id()` in router handles this |
| Profile page shows no cards | `localStorage` key mismatch | Fixed — context reads `access_token` key |
| Manage Items drawer shows no items | `GET /menu-items` returned empty | Check that seed ran; confirm `menu_items` table has rows |
| Item assigned but not visible in sidebar | Item is inactive | Activate it via Menu Items page |
