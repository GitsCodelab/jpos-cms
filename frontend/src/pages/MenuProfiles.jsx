import React, { useEffect, useState } from 'react'
import {
  Card,
  Row,
  Col,
  Typography,
  Badge,
  Button,
  Spin,
  Space,
  Tag,
  Popconfirm,
  message,
  Drawer,
  Transfer,
} from 'antd'
import {
  AppstoreOutlined,
  CheckOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import menuAPI from '../services/menuApi'
import { useMenu } from '../store/MenuContext'

const { Title, Text, Paragraph } = Typography

export default function MenuProfiles() {
  const { currentMenu, selectProfile, loading: ctxLoading, refreshMenu } = useMenu()

  const [profiles, setProfiles] = useState([])
  const [loadingProfiles, setLoadingProfiles] = useState(false)
  const [selecting, setSelecting] = useState(null)
  const [toggling, setToggling] = useState(null)

  // Manage-items drawer state
  const [drawerProfile, setDrawerProfile] = useState(null)   // profile being managed
  const [allItems, setAllItems] = useState([])               // all top-level items (flat)
  const [assignedIds, setAssignedIds] = useState([])         // currently assigned item IDs
  const [drawerLoading, setDrawerLoading] = useState(false)
  const [drawerSaving, setDrawerSaving] = useState(false)

  const loadProfiles = async () => {
    setLoadingProfiles(true)
    try {
      const res = await menuAPI.getAllProfilesAdmin()
      setProfiles(res.data)
    } catch {
      message.error('Failed to load profiles')
    } finally {
      setLoadingProfiles(false)
    }
  }

  useEffect(() => {
    loadProfiles()
  }, [])

  const handleSelect = async (profileId) => {
    setSelecting(profileId)
    try {
      await selectProfile(profileId)
      message.success('Profile selected')
    } catch {
      message.error('Failed to select profile')
    } finally {
      setSelecting(null)
    }
  }

  const handleToggleActive = async (profile) => {
    setToggling(profile.id)
    try {
      if (profile.is_active) {
        await menuAPI.deactivateProfile(profile.id)
        message.success(`"${profile.display_name}" deactivated`)
      } else {
        await menuAPI.activateProfile(profile.id)
        message.success(`"${profile.display_name}" activated`)
      }
      await loadProfiles()
    } catch {
      message.error('Failed to update profile status')
    } finally {
      setToggling(null)
    }
  }

  const openManageItems = async (profile) => {
    setDrawerProfile(profile)
    setDrawerLoading(true)
    try {
      const [itemsRes, idsRes] = await Promise.all([
        menuAPI.getAllItems(),
        menuAPI.getProfileItemIds(profile.id),
      ])
      // Only top-level items (parent_id === null)
      const topLevel = (itemsRes.data || []).filter((i) => i.parent_id === null)
      setAllItems(topLevel)
      setAssignedIds(idsRes.data || [])
    } catch {
      message.error('Failed to load menu items')
    } finally {
      setDrawerLoading(false)
    }
  }

  const closeDrawer = () => {
    setDrawerProfile(null)
    setAllItems([])
    setAssignedIds([])
    setDrawerSaving(false)
  }

  const handleTransferChange = async (nextTargetKeys, direction, movedKeys) => {
    setDrawerSaving(true)
    try {
      if (direction === 'right') {
        // adding items
        await Promise.all(
          movedKeys.map((id) => menuAPI.addItemToProfile(drawerProfile.id, id))
        )
      } else {
        // removing items
        await Promise.all(
          movedKeys.map((id) => menuAPI.removeItemFromProfile(drawerProfile.id, id))
        )
      }
      setAssignedIds(nextTargetKeys)
      message.success('Profile items updated')
    } catch {
      message.error('Failed to update profile items')
    } finally {
      setDrawerSaving(false)
    }
  }

  if (loadingProfiles && profiles.length === 0) {
    return (
      <div style={{ padding: 32, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    )
  }

  const currentProfileId = currentMenu?.id

  return (
    <div style={{ padding: '24px 32px', maxWidth: 1200 }}>
      {/* Page header */}
      <div style={{ marginBottom: 24 }}>
        <Space align="center" size={10}>
          <AppstoreOutlined style={{ fontSize: 22, color: '#0a6ed1' }} />
          <Title level={4} style={{ margin: 0 }}>
            Menu Profiles
          </Title>
        </Space>
        <Paragraph type="secondary" style={{ marginTop: 4, marginBottom: 0 }}>
          Select a menu layout profile to customise your sidebar navigation. Administrators can
          activate or deactivate profiles.
        </Paragraph>
      </div>

      {/* Profile cards */}
      <Row gutter={[20, 20]}>
        {profiles.map((profile) => {
          const isSelected = profile.id === currentProfileId
          const isSelecting = selecting === profile.id
          const isToggling = toggling === profile.id

          return (
            <Col xs={24} sm={12} lg={8} key={profile.id}>
              <Card
                style={{
                  borderRadius: 8,
                  border: isSelected
                    ? '2px solid #0a6ed1'
                    : !profile.is_active
                    ? '1px dashed #d9d9d9'
                    : '1px solid #d8dce6',
                  boxShadow: isSelected ? '0 2px 12px rgba(10,110,209,0.12)' : 'none',
                  opacity: profile.is_active ? 1 : 0.65,
                  transition: 'all 0.2s',
                  height: '100%',
                }}
                bodyStyle={{ padding: 20 }}
              >
                {/* Header row */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: 8,
                  }}
                >
                  <Text strong style={{ fontSize: 15 }}>
                    {profile.display_name}
                  </Text>

                  <Space size={4} wrap>
                    {profile.is_default && (
                      <Tag color="blue" style={{ margin: 0, fontSize: 11 }}>
                        Default
                      </Tag>
                    )}
                    <Tag
                      color={profile.is_active ? 'success' : 'default'}
                      style={{ margin: 0, fontSize: 11 }}
                    >
                      {profile.is_active ? 'Active' : 'Inactive'}
                    </Tag>
                    {isSelected && profile.is_active && (
                      <Badge
                        status="processing"
                        text={
                          <Text style={{ fontSize: 11, color: '#0a6ed1' }}>Selected</Text>
                        }
                      />
                    )}
                  </Space>
                </div>

                {/* Description */}
                <Paragraph
                  type="secondary"
                  style={{ fontSize: 12, minHeight: 40, marginBottom: 16 }}
                >
                  {profile.description || 'No description.'}
                </Paragraph>

                {/* Actions */}
                <Space size={8}>
                  {/* Select button — only shown for active profiles */}
                  {profile.is_active && (
                    <Button
                      type={isSelected ? 'default' : 'primary'}
                      size="small"
                      icon={isSelected ? <CheckOutlined /> : null}
                      loading={isSelecting}
                      disabled={isSelected}
                      onClick={() => handleSelect(profile.id)}
                      style={
                        isSelected
                          ? {
                              backgroundColor: '#52c41a',
                              borderColor: '#52c41a',
                              color: '#fff',
                              cursor: 'default',
                            }
                          : {}
                      }
                    >
                      {isSelected ? 'Selected' : 'Select'}
                    </Button>
                  )}

                  {/* Activate / Deactivate */}
                  {profile.is_active ? (
                    <Popconfirm
                      title={`Deactivate "${profile.display_name}"?`}
                      description="Users on this profile will fall back to the default."
                      okText="Deactivate"
                      okType="danger"
                      cancelText="Cancel"
                      onConfirm={() => handleToggleActive(profile)}
                    >
                      <Button
                        size="small"
                        danger
                        icon={<PauseCircleOutlined />}
                        loading={isToggling}
                        disabled={profile.is_default}
                      >
                        Deactivate
                      </Button>
                    </Popconfirm>
                  ) : (
                    <Button
                      size="small"
                      icon={<PlayCircleOutlined />}
                      loading={isToggling}
                      onClick={() => handleToggleActive(profile)}
                      style={{ borderColor: '#52c41a', color: '#52c41a' }}
                    >
                      Activate
                    </Button>
                  )}
                  <Button
                    size="small"
                    icon={<UnorderedListOutlined />}
                    onClick={() => openManageItems(profile)}
                  >
                    Manage Items
                  </Button>
                </Space>
              </Card>
            </Col>
          )
        })}
      </Row>

      {/* ── Manage Items Drawer ─────────────────────────────────────── */}
      <Drawer
        title={drawerProfile ? `Manage Items — ${drawerProfile.display_name}` : ''}
        width={640}
        open={!!drawerProfile}
        onClose={closeDrawer}
        destroyOnClose
      >
        {drawerLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin />
          </div>
        ) : (
          <Transfer
            dataSource={allItems.map((item) => ({
              key: item.id,
              title: item.label,
              description: item.key,
            }))}
            targetKeys={assignedIds}
            onChange={handleTransferChange}
            render={(item) => (
              <span>
                <Text strong>{item.title}</Text>
                <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                  {item.description}
                </Text>
              </span>
            )}
            showSearch
            filterOption={(input, item) =>
              item.title.toLowerCase().includes(input.toLowerCase()) ||
              item.description.toLowerCase().includes(input.toLowerCase())
            }
            listStyle={{ width: 260, height: 420 }}
            titles={['Available', 'Assigned']}
            disabled={drawerSaving}
          />
        )}
      </Drawer>
    </div>
  )
}
