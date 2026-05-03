/**
 * MenuContext.jsx — React Context providing dynamic menu state.
 *
 * Exposes:
 *   - menuProfiles    : List<MenuProfileResponse>
 *   - currentProfile  : MenuProfileResponse | null
 *   - currentMenu     : MenuProfileWithMenusResponse | null  (contains .menus array)
 *   - loading         : boolean
 *   - error           : string | null
 *   - fetchCurrentMenu()
 *   - selectProfile(profileId)
 *
 * Wrap your route tree with <MenuProvider> after the user is authenticated.
 * Use the useMenu() hook to consume context anywhere in the tree.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import menuAPI from '../services/menuApi'

const MenuContext = createContext(null)

export function MenuProvider({ children }) {
  const [menuProfiles, setMenuProfiles] = useState([])
  const [currentMenu, setCurrentMenu] = useState(null)
  const [currentProfile, setCurrentProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchCurrentMenu = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [menuRes, profilesRes] = await Promise.all([
        menuAPI.getCurrentMenu(),
        menuAPI.getProfiles(),
      ])
      setCurrentMenu(menuRes.data)
      setCurrentProfile(menuRes.data)   // root is the profile itself (contains menus)
      setMenuProfiles(profilesRes.data)
    } catch (err) {
      console.error('[MenuContext] Failed to load menu:', err)
      setError('Failed to load menu')
    } finally {
      setLoading(false)
    }
  }, [])

  const selectProfile = useCallback(async (profileId) => {
    setLoading(true)
    setError(null)
    try {
      await menuAPI.selectProfile(profileId)
      await fetchCurrentMenu()
    } catch (err) {
      console.error('[MenuContext] Failed to select profile:', err)
      setError('Failed to select profile')
      setLoading(false)
    }
  }, [fetchCurrentMenu])

  // Load on mount — only if the user is logged in (token present)
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchCurrentMenu()
    }
  }, [fetchCurrentMenu])

  return (
    <MenuContext.Provider
      value={{
        menuProfiles,
        currentMenu,
        currentProfile,
        loading,
        error,
        fetchCurrentMenu,
        selectProfile,
      }}
    >
      {children}
    </MenuContext.Provider>
  )
}

/**
 * Hook to consume MenuContext. Must be used inside <MenuProvider>.
 */
export function useMenu() {
  const ctx = useContext(MenuContext)
  if (!ctx) {
    throw new Error('useMenu must be used within a MenuProvider')
  }
  return ctx
}

export default MenuContext
