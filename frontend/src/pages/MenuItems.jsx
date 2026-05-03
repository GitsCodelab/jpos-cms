import React, { useEffect, useState, useMemo } from 'react'
import {
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Popconfirm,
  message,
  Tooltip,
  Select,
  AutoComplete,
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  StopOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import menuAPI from '../services/menuApi'

const { Title, Paragraph } = Typography
const { Option } = Select

// All Ant Design icon names available in seed data
const ICON_OPTIONS = [
  'ApiOutlined', 'AppstoreAddOutlined', 'AppstoreOutlined', 'AuditOutlined',
  'BankOutlined', 'BarChartOutlined', 'BellOutlined', 'BlockOutlined',
  'BookOutlined', 'BranchesOutlined', 'BugOutlined', 'CalendarOutlined',
  'CheckSquareOutlined', 'ClusterOutlined', 'ContainerOutlined', 'CreditCardOutlined',
  'CrownOutlined', 'CustomerServiceOutlined', 'DashboardOutlined', 'DatabaseOutlined',
  'DesktopOutlined', 'DollarOutlined', 'ExceptionOutlined', 'FileOutlined',
  'FileProtectOutlined', 'FileSearchOutlined', 'FileTextOutlined', 'FolderOutlined',
  'FormOutlined', 'FundOutlined', 'GlobalOutlined', 'IdcardOutlined',
  'LockOutlined', 'MonitorOutlined', 'NotificationOutlined', 'OrderedListOutlined',
  'PhoneOutlined', 'PieChartOutlined', 'ReconciliationOutlined', 'RetweetOutlined',
  'RiseOutlined', 'SafetyOutlined', 'ScheduleOutlined', 'SendOutlined',
  'SettingOutlined', 'ShopOutlined', 'SlidersOutlined', 'StopOutlined',
  'SyncOutlined', 'TagOutlined', 'TagsOutlined', 'TeamOutlined', 'ToolOutlined',
  'TransactionOutlined', 'UnorderedListOutlined',
]

// Common permission/role patterns
const BASE_PERMISSIONS = [
  'admin', 'admin.view', 'admin.write',
  'fraud.view', 'fraud.write',
  'reconciliation.view', 'reconciliation.write',
  'settlement.view', 'settlement.write',
  'transactions.view', 'transactions.write',
  'reports.view', 'reports.write',
  'configuration.view', 'configuration.write',
  'monitoring.view', 'monitoring.write',
  'operations.view', 'operations.write',
]

export default function MenuItems() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [actionTarget, setActionTarget] = useState(null)

  const [form] = Form.useForm()
  const [iconSearch, setIconSearch] = useState('')

  const loadItems = async () => {
    setLoading(true)
    try {
      const res = await menuAPI.getAllItems()
      setItems(res.data)
    } catch {
      message.error('Failed to load menu items')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadItems()
  }, [])

  // Build key options from existing items (for dropdown)
  const existingKeys = useMemo(() => items.map((i) => i.key), [items])

  // Filtered icon options based on search
  const filteredIcons = useMemo(
    () =>
      ICON_OPTIONS.filter((icon) =>
        icon.toLowerCase().includes(iconSearch.toLowerCase())
      ),
    [iconSearch]
  )

  // Permission options: base list + any custom ones from existing items
  const permissionOptions = useMemo(() => {
    const fromItems = items
      .map((i) => i.permission)
      .filter(Boolean)
      .filter((p) => !BASE_PERMISSIONS.includes(p))
    return [...BASE_PERMISSIONS, ...fromItems]
  }, [items])

  // Build nested tree from flat list for the Table
  const treeData = useMemo(() => {
    const map = {}
    items.forEach((item) => { map[item.id] = { ...item, children: [] } })
    const roots = []
    items.forEach((item) => {
      if (item.parent_id && map[item.parent_id]) {
        map[item.parent_id].children.push(map[item.id])
      } else {
        roots.push(map[item.id])
      }
    })
    // Remove empty children arrays (Ant Design expands only when children exist)
    const clean = (nodes) =>
      nodes.map((n) => ({
        ...n,
        children: n.children.length > 0 ? clean(n.children) : undefined,
      }))
    return clean(roots)
  }, [items])

  const handleCreate = async (values) => {
    setSaving(true)
    try {
      await menuAPI.createItem(values)
      message.success('Menu item created')
      setModalOpen(false)
      form.resetFields()
      loadItems()
    } catch (err) {
      const detail = err?.response?.data?.detail
      message.error(detail || 'Failed to create menu item')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (itemId) => {
    setActionTarget(itemId)
    try {
      await menuAPI.deleteItem(itemId)
      message.success('Menu item deleted')
      loadItems()
    } catch {
      message.error('Failed to delete menu item')
    } finally {
      setActionTarget(null)
    }
  }

  const handleToggle = async (item) => {
    setActionTarget(item.id)
    try {
      if (item.is_active) {
        await menuAPI.deactivateItem(item.id)
        message.success(`"${item.label}" deactivated`)
      } else {
        await menuAPI.activateItem(item.id)
        message.success(`"${item.label}" activated`)
      }
      loadItems()
    } catch {
      message.error('Failed to update item status')
    } finally {
      setActionTarget(null)
    }
  }

  const columns = [
    {
      title: 'Key (Route)',
      dataIndex: 'key',
      key: 'key',
      render: (val) => <code style={{ fontSize: 12 }}>{val}</code>,
    },
    {
      title: 'Label',
      dataIndex: 'label',
      key: 'label',
    },
    {
      title: 'Icon',
      dataIndex: 'icon_name',
      key: 'icon_name',
      render: (val) =>
        val ? (
          <code style={{ fontSize: 12 }}>{val}</code>
        ) : (
          <span style={{ color: '#bbb' }}>—</span>
        ),
    },
    {
      title: 'Permission / Role',
      dataIndex: 'permission',
      key: 'permission',
      render: (val) =>
        val ? (
          <Tag color="geekblue" style={{ fontSize: 11 }}>
            {val}
          </Tag>
        ) : (
          <span style={{ color: '#bbb' }}>—</span>
        ),
    },
    {
      title: 'Group',
      dataIndex: 'is_group',
      key: 'is_group',
      align: 'center',
      render: (val) =>
        val ? (
          <Tag color="purple" style={{ fontSize: 11 }}>
            Group
          </Tag>
        ) : (
          <Tag color="default" style={{ fontSize: 11 }}>
            Item
          </Tag>
        ),
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      align: 'center',
      render: (val) =>
        val ? (
          <Tag color="success" style={{ fontSize: 11 }}>
            Active
          </Tag>
        ) : (
          <Tag color="default" style={{ fontSize: 11 }}>
            Inactive
          </Tag>
        ),
    },
    {
      title: 'Order',
      dataIndex: 'order_index',
      key: 'order_index',
      align: 'center',
      width: 70,
    },
    {
      title: 'Actions',
      key: 'actions',
      align: 'center',
      render: (_, record) => {
        const busy = actionTarget === record.id
        return (
          <Space size={6}>
            <Tooltip title={record.is_active ? 'Deactivate' : 'Activate'}>
              <Button
                size="small"
                icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
                loading={busy}
                onClick={() => handleToggle(record)}
                style={
                  record.is_active
                    ? { color: '#faad14', borderColor: '#faad14' }
                    : { color: '#52c41a', borderColor: '#52c41a' }
                }
              />
            </Tooltip>
            <Popconfirm
              title="Delete this menu item?"
              description="This cannot be undone."
              okText="Delete"
              okType="danger"
              cancelText="Cancel"
              onConfirm={() => handleDelete(record.id)}
            >
              <Tooltip title="Delete">
                <Button size="small" danger icon={<DeleteOutlined />} loading={busy} />
              </Tooltip>
            </Popconfirm>
          </Space>
        )
      },
    },
  ]

  return (
    <div style={{ padding: '24px 32px', maxWidth: 1400 }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 20,
        }}
      >
        <div>
          <Space align="center" size={10}>
            <UnorderedListOutlined style={{ fontSize: 22, color: '#0a6ed1' }} />
            <Title level={4} style={{ margin: 0 }}>
              Menu Items
            </Title>
          </Space>
          <Paragraph type="secondary" style={{ marginTop: 4, marginBottom: 0 }}>
            Manage top-level navigation items. Items can be activated, deactivated, or removed.
          </Paragraph>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            form.resetFields()
            setIconSearch('')
            setModalOpen(true)
          }}
        >
          Add Item
        </Button>
      </div>

      {/* Table */}
      <Table
        rowKey="id"
        dataSource={treeData}
        columns={columns}
        loading={loading}
        size="small"
        pagination={false}
        scroll={{ y: 600 }}
        defaultExpandAllRows={false}
      />

      {/* Create modal */}
      <Modal
        title="Add Menu Item"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        okText="Create"
        confirmLoading={saving}
        destroyOnClose
        width={540}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ order_index: 0, is_group: false }}
          style={{ marginTop: 16 }}
        >
          {/* Key — autocomplete from existing keys */}
          <Form.Item
            name="key"
            label="Key (Route)"
            extra="Route path like /my-page or group key like my-group"
            rules={[{ required: true, message: 'Key is required' }]}
          >
            <AutoComplete
              options={existingKeys.map((k) => ({ value: k }))}
              filterOption={(input, option) =>
                option.value.toLowerCase().includes(input.toLowerCase())
              }
              allowClear
            >
              <Input placeholder="/my-page" maxLength={200} />
            </AutoComplete>
          </Form.Item>

          {/* Label */}
          <Form.Item
            name="label"
            label="Label"
            rules={[{ required: true, message: 'Label is required' }]}
          >
            <Input placeholder="My Page" maxLength={200} />
          </Form.Item>

          {/* Icon — searchable dropdown */}
          <Form.Item name="icon_name" label="Icon">
            <Select
              showSearch
              allowClear
              placeholder="Search icon name…"
              onSearch={setIconSearch}
              filterOption={(input, option) =>
                option.value.toLowerCase().includes(input.toLowerCase())
              }
              optionLabelProp="value"
            >
              {ICON_OPTIONS.map((icon) => (
                <Option key={icon} value={icon}>
                  <code style={{ fontSize: 12 }}>{icon}</code>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* Permission — searchable dropdown with common values */}
          <Form.Item name="permission" label="Permission / Role">
            <Select
              showSearch
              allowClear
              placeholder="Select or type a permission…"
              filterOption={(input, option) =>
                option.value.toLowerCase().includes(input.toLowerCase())
              }
              mode="combobox"
            >
              {permissionOptions.map((p) => (
                <Option key={p} value={p}>
                  {p}
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* Order index */}
          <Form.Item name="order_index" label="Order Index">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          {/* Is group */}
          <Form.Item name="is_group" label="Is Group (has children)" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
