/**
 * menuApi.js — API calls for dynamic menu profiles.
 */

import api from './api'

const menuAPI = {
  // ── Profile user-facing ──────────────────────────────────────────────────
  /** List all active menu profiles */
  getProfiles: () => api.get('/menu-profiles'),

  /** Get a profile's full nested menu tree */
  getProfileMenus: (profileId) => api.get(`/menu-profiles/${profileId}/menus`),

  /** Set the current user's menu profile */
  selectProfile: (profileId) => api.post('/menu-profiles/select', { profile_id: profileId }),

  /** Get the current user's resolved menu tree */
  getCurrentMenu: () => api.get('/menu/current'),

  // ── Profile admin ─────────────────────────────────────────────────────────
  /** List ALL profiles including inactive ones */
  getAllProfilesAdmin: () => api.get('/menu-profiles/admin/all'),

  /** Activate a menu profile */
  activateProfile: (profileId) => api.patch(`/menu-profiles/${profileId}/activate`),

  /** Deactivate a menu profile */
  deactivateProfile: (profileId) => api.patch(`/menu-profiles/${profileId}/deactivate`),

  // ── Menu items admin ───────────────────────────────────────────────────────
  /** List all top-level menu items */
  getAllItems: () => api.get('/menu-items'),

  /** Create a new top-level menu item */
  createItem: (payload) => api.post('/menu-items', payload),

  /** Delete a menu item by id */
  deleteItem: (itemId) => api.delete(`/menu-items/${itemId}`),

  /** Activate a menu item */
  activateItem: (itemId) => api.patch(`/menu-items/${itemId}/activate`),

  /** Deactivate a menu item */
  deactivateItem: (itemId) => api.patch(`/menu-items/${itemId}/deactivate`),

  // ── Profile-item assignment ────────────────────────────────────────────────
  /** List item IDs assigned to a profile */
  getProfileItemIds: (profileId) => api.get(`/menu-profiles/${profileId}/items`),

  /** Assign a top-level item to a profile */
  addItemToProfile: (profileId, itemId) =>
    api.post(`/menu-profiles/${profileId}/items`, { item_id: itemId }),

  /** Remove an item from a profile */
  removeItemFromProfile: (profileId, itemId) =>
    api.delete(`/menu-profiles/${profileId}/items/${itemId}`),
}

export default menuAPI
