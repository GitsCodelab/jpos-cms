import React, { useState, useMemo, useCallback } from 'react'
import { Layout, Menu, Input, Tabs, Badge, Button, Tooltip, Typography, Empty } from 'antd'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  AppstoreOutlined,
  SearchOutlined,
  BookOutlined,
  StarFilled,
  StarOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import menuConfig, { flattenMenuItems, findAncestorKeys } from '../../config/menuConfig'

const { Sider } = Layout
const { Text } = Typography

const BOOKMARKS_STORAGE_KEY = 'jpos_cms_bookmarks'

const loadBookmarks = () => {
  try {
    return JSON.parse(localStorage.getItem(BOOKMARKS_STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

const persistBookmarks = (bookmarks) => {
  localStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(bookmarks))
}

/**
 * Recursively builds Ant Design Menu items from the config tree.
 * Leaf items get a star/bookmark toggle appended to their label.
 */
const buildAntMenuItems = (items, onToggleBookmark, bookmarkedKeys, hideBookmarkToggle = false) =>
  items.map((item) => {
    if (item.children && item.children.length > 0) {
      return {
        key: item.key,
        icon: item.icon,
        label: item.label,
        children: buildAntMenuItems(item.children, onToggleBookmark, bookmarkedKeys, hideBookmarkToggle),
      }
    }

    const isBookmarked = bookmarkedKeys.includes(item.key)

    return {
      key: item.key,
      icon: item.icon,
      label: hideBookmarkToggle ? (
        item.label
      ) : (
        <span style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 4 }}>
          <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {item.label}
          </span>
          <span
            role="button"
            aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
            onClick={(e) => {
              e.stopPropagation()
              onToggleBookmark(item.key)
            }}
            style={{ color: isBookmarked ? '#e3a821' : '#d8dce6', cursor: 'pointer', flexShrink: 0 }}
          >
            {isBookmarked ? <StarFilled style={{ fontSize: 11 }} /> : <StarOutlined style={{ fontSize: 11 }} />}
          </span>
        </span>
      ),
    }
  })

export default function Sidebar({ collapsed, onCollapse }) {
  const navigate = useNavigate()
  const location = useLocation()

  const [activeTab, setActiveTab] = useState('menu')
  const [searchQuery, setSearchQuery] = useState('')
  const [bookmarkedKeys, setBookmarkedKeys] = useState(loadBookmarks)
  const [openKeys, setOpenKeys] = useState(() => findAncestorKeys(menuConfig, location.pathname) || [])

  const allLeafItems = useMemo(() => flattenMenuItems(), [])

  const toggleBookmark = useCallback((key) => {
    setBookmarkedKeys((prev) => {
      const next = prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
      persistBookmarks(next)
      return next
    })
  }, [])

  // Full menu items (with bookmark toggles)
  const menuItems = useMemo(
    () => buildAntMenuItems(menuConfig, toggleBookmark, bookmarkedKeys),
    [bookmarkedKeys, toggleBookmark],
  )

  // Collapsed icon-only menu – no bookmark star (no room)
  const collapsedMenuItems = useMemo(
    () => buildAntMenuItems(menuConfig, toggleBookmark, bookmarkedKeys, true),
    [bookmarkedKeys, toggleBookmark],
  )

  const filteredSearchItems = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return []
    return allLeafItems
      .filter((item) => item.label.toLowerCase().includes(q))
      .map((item) => ({ key: item.key, icon: item.icon, label: item.label }))
  }, [searchQuery, allLeafItems])

  const bookmarkedMenuItems = useMemo(
    () =>
      allLeafItems
        .filter((item) => bookmarkedKeys.includes(item.key))
        .map((item) => ({
          key: item.key,
          icon: item.icon,
          label: (
            <span style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 4 }}>
              <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.label}
              </span>
              <StarFilled
                role="button"
                aria-label="Remove bookmark"
                onClick={(e) => { e.stopPropagation(); toggleBookmark(item.key) }}
                style={{ color: '#e3a821', cursor: 'pointer', flexShrink: 0, fontSize: 11 }}
              />
            </span>
          ),
        })),
    [bookmarkedKeys, allLeafItems, toggleBookmark],
  )

  const handleMenuSelect = useCallback(
    ({ key }) => { if (key.startsWith('/')) navigate(key) },
    [navigate],
  )

  // Keep open keys in sync when navigating programmatically
  const handleOpenChange = useCallback((keys) => setOpenKeys(keys), [])

  const selectedKey = location.pathname

  const tabItems = [
    {
      key: 'menu',
      label: (
        <Tooltip title="Menu" placement="right">
          <AppstoreOutlined />
        </Tooltip>
      ),
    },
    {
      key: 'bookmarks',
      label: (
        <Tooltip title="Bookmarks" placement="right">
          <Badge count={bookmarkedKeys.length} size="small" color="#0a6ed1" offset={[6, -2]}>
            <BookOutlined />
          </Badge>
        </Tooltip>
      ),
    },
    {
      key: 'search',
      label: (
        <Tooltip title="Search" placement="right">
          <SearchOutlined />
        </Tooltip>
      ),
    },
  ]

  return (
    <Sider
      width={260}
      collapsedWidth={48}
      collapsed={collapsed}
      style={{
        background: '#ffffff',
        borderRight: '1px solid #d8dce6',
        height: '100%',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        userSelect: 'none',
      }}
    >
      {/* ── Collapse toggle ─────────────────────────────────── */}
      <div
        style={{
          height: 36,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-end',
          padding: '0 6px',
          borderBottom: '1px solid #f0f0f0',
          flexShrink: 0,
        }}
      >
        <Tooltip title={collapsed ? 'Expand' : 'Collapse'} placement="right">
          <Button
            type="text"
            size="small"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => onCollapse(!collapsed)}
            style={{ color: '#666' }}
          />
        </Tooltip>
      </div>

      {/* ── Tab strip (hidden when collapsed) ───────────────── */}
      {!collapsed && (
        <div style={{ flexShrink: 0, borderBottom: '1px solid #f0f0f0' }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            size="small"
            tabBarStyle={{ margin: 0, padding: '0 12px' }}
            items={tabItems}
          />
        </div>
      )}

      {/* ── Scrollable body ──────────────────────────────────── */}
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>

        {/* Menu tab — also shown when collapsed (icon-only) */}
        {(activeTab === 'menu' || collapsed) && (
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            openKeys={collapsed ? [] : openKeys}
            onOpenChange={handleOpenChange}
            items={collapsed ? collapsedMenuItems : menuItems}
            onSelect={handleMenuSelect}
            inlineCollapsed={collapsed}
            style={{ border: 'none' }}
          />
        )}

        {/* Bookmarks tab */}
        {!collapsed && activeTab === 'bookmarks' && (
          bookmarkedMenuItems.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              style={{ margin: '32px 0' }}
              description={
                <Text style={{ fontSize: 11, color: '#999' }}>
                  No bookmarks yet.<br />Star any menu item to pin it here.
                </Text>
              }
            />
          ) : (
            <Menu
              mode="inline"
              selectedKeys={[selectedKey]}
              items={bookmarkedMenuItems}
              onSelect={handleMenuSelect}
              style={{ border: 'none' }}
            />
          )
        )}

        {/* Search tab */}
        {!collapsed && activeTab === 'search' && (
          <div style={{ padding: '8px 8px 0' }}>
            <Input
              placeholder="Search menu…"
              prefix={<SearchOutlined style={{ color: '#aaa' }} />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              allowClear
              size="small"
              autoFocus
              style={{ marginBottom: 4 }}
            />
            {searchQuery.trim() && (
              filteredSearchItems.length === 0 ? (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  style={{ margin: '24px 0' }}
                  description={<Text style={{ fontSize: 11, color: '#999' }}>No results found</Text>}
                />
              ) : (
                <Menu
                  mode="inline"
                  selectedKeys={[selectedKey]}
                  items={filteredSearchItems}
                  onSelect={handleMenuSelect}
                  style={{ border: 'none' }}
                />
              )
            )}
          </div>
        )}
      </div>
    </Sider>
  )
}
