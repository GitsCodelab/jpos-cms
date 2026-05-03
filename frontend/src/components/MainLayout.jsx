import React, { useState } from 'react'
import { Layout, Avatar, Space, Tag, Dropdown, Typography, Button } from 'antd'
import {
  UserOutlined,
  DownOutlined,
  LogoutOutlined,
  KeyOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import { useMenu } from '../store/MenuContext'

const { Header, Content } = Layout
const { Text } = Typography

const getUserFromStorage = () => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
}

const ROLE_COLORS = {
  admin: 'blue',
  operator: 'green',
  viewer: 'default',
}

export default function MainLayout({ onLogout }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const navigate = useNavigate()
  const user = getUserFromStorage()
  const { currentMenu } = useMenu()

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'My Profile',
    },
    {
      key: 'change-password',
      icon: <KeyOutlined />,
      label: 'Change Password',
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sign Out',
      danger: true,
    },
  ]

  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') onLogout()
    if (key === 'change-password') navigate('/settings/change-password')
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* ── Top Header ─────────────────────────────────────────── */}
      <Header
        style={{
          background: '#0a6ed1',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 16px',
          height: 44,
          lineHeight: '44px',
          position: 'sticky',
          top: 0,
          zIndex: 200,
          boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
        }}
      >
        {/* Left: Logo */}
        <Space size={8}>
          <Text style={{ color: '#ffffff', fontWeight: 700, fontSize: 15, letterSpacing: 0.5 }}>
            jPOS CMS
          </Text>
          <Tag
            style={{
              background: 'rgba(255,255,255,0.15)',
              border: '1px solid rgba(255,255,255,0.3)',
              color: '#fff',
              fontSize: 10,
              lineHeight: '16px',
              padding: '0 5px',
            }}
          >
            v1.0
          </Tag>
        </Space>

        {/* Right: User menu */}
        <Dropdown
          menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
          trigger={['click']}
          placement="bottomRight"
        >
          <Button
            type="text"
            style={{ color: '#fff', height: 44, padding: '0 8px' }}
          >
            <Space size={6}>
              <Avatar
                size={24}
                icon={<UserOutlined />}
                style={{ background: 'rgba(255,255,255,0.25)', color: '#fff' }}
              />
              <Text style={{ color: '#fff', fontSize: 12 }}>
                {user.username || 'admin'}
              </Text>
              <Tag
                color={ROLE_COLORS[user.role] || 'default'}
                style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}
              >
                {user.role || 'admin'}
              </Tag>
              <DownOutlined style={{ fontSize: 9 }} />
            </Space>
          </Button>
        </Dropdown>
      </Header>

      {/* ── Body: Sidebar + Content ─────────────────────────────── */}
      <Layout style={{ height: 'calc(100vh - 44px)', minHeight: 0 }}>
        <Sidebar
          collapsed={sidebarCollapsed}
          onCollapse={setSidebarCollapsed}
          menuData={currentMenu?.menus}
        />

        <Content
          style={{
            background: '#f5f6f7',
            overflowY: 'auto',
            overflowX: 'hidden',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
