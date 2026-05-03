import { useEffect, useState } from 'react'
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Tooltip,
  Typography,
  message,
} from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  EditOutlined,
  LoadingOutlined,
  PlusOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { dbConnectionAPI } from '../services/api'

const { Title, Text } = Typography
const { Option } = Select

const DB_TYPE_COLORS = {
  ORACLE: 'red',
  POSTGRESQL: 'blue',
}

const DEFAULT_PORTS = {
  ORACLE: 1521,
  POSTGRESQL: 5432,
}

// ---------------------------------------------------------------------------
// Add / Edit Modal Form
// ---------------------------------------------------------------------------

function ConnectionFormModal({ open, connection, onSuccess, onCancel }) {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const isEdit = !!connection

  useEffect(() => {
    if (open) {
      if (connection) {
        form.setFieldsValue({
          connection_name: connection.connection_name,
          database_type: connection.database_type,
          host: connection.host,
          port: connection.port,
          service_name: connection.service_name,
          username: connection.username,
          schema_name: connection.schema_name || '',
          description: connection.description || '',
          is_active: connection.is_active,
          password: '',
        })
      } else {
        form.resetFields()
        form.setFieldValue('is_active', true)
        form.setFieldValue('database_type', 'POSTGRESQL')
        form.setFieldValue('port', DEFAULT_PORTS.POSTGRESQL)
      }
      setError('')
    }
  }, [open, connection, form])

  const handleDbTypeChange = (value) => {
    form.setFieldValue('port', DEFAULT_PORTS[value] || '')
  }

  const onFinish = async (values) => {
    setLoading(true)
    setError('')
    try {
      if (isEdit) {
        const payload = { ...values }
        if (!payload.password) delete payload.password
        await dbConnectionAPI.update(connection.id, payload)
        message.success('Connection updated successfully.')
      } else {
        await dbConnectionAPI.create(values)
        message.success('Connection created successfully.')
      }
      onSuccess()
    } catch (err) {
      const detail = err?.response?.data?.detail || 'An error occurred.'
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={
        <Space>
          <DatabaseOutlined />
          {isEdit ? 'Edit Connection' : 'Add New Connection'}
        </Space>
      }
      open={open}
      onCancel={onCancel}
      onOk={() => form.submit()}
      okText={isEdit ? 'Save Changes' : 'Create Connection'}
      confirmLoading={loading}
      width={640}
      destroyOnClose
    >
      {error && (
        <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />
      )}
      <Form form={form} layout="vertical" onFinish={onFinish} autoComplete="off">
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="connection_name"
              label="Connection Name"
              rules={[{ required: true, message: 'Connection name is required.' }]}
            >
              <Input placeholder="e.g. Oracle SmartVista Production" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="database_type"
              label="Database Type"
              rules={[{ required: true, message: 'Database type is required.' }]}
            >
              <Select onChange={handleDbTypeChange}>
                <Option value="ORACLE">Oracle</Option>
                <Option value="POSTGRESQL">PostgreSQL</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="port"
              label="Port"
              rules={[{ required: true, message: 'Port is required.' }]}
            >
              <InputNumber min={1} max={65535} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={16}>
            <Form.Item
              name="host"
              label="Host"
              rules={[{ required: true, message: 'Host is required.' }]}
            >
              <Input placeholder="e.g. 192.168.1.100 or db.internal" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="service_name"
              label="Service / Database Name"
              rules={[{ required: true, message: 'Service name is required.' }]}
            >
              <Input placeholder="e.g. xepdb1 or mydb" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="username"
              label="Username"
              rules={[{ required: true, message: 'Username is required.' }]}
            >
              <Input autoComplete="new-password" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="password"
              label={isEdit ? 'New Password (leave blank to keep current)' : 'Password'}
              rules={
                isEdit
                  ? []
                  : [{ required: true, message: 'Password is required.' }]
              }
            >
              <Input.Password autoComplete="new-password" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="schema_name" label="Schema (optional)">
              <Input placeholder="e.g. MAIN" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="is_active" label="Active" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item name="description" label="Description (optional)">
          <Input.TextArea rows={2} placeholder="Brief description of this connection" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Test Result Modal
// ---------------------------------------------------------------------------

function TestResultModal({ open, result, onClose }) {
  if (!result) return null
  return (
    <Modal
      title="Connection Test Result"
      open={open}
      onCancel={onClose}
      footer={<Button onClick={onClose}>Close</Button>}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <Alert
          type={result.success ? 'success' : 'error'}
          message={result.success ? 'Connection Successful' : 'Connection Failed'}
          description={result.message}
          icon={result.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          showIcon
        />
        {result.latency_ms != null && (
          <Text type="secondary">Latency: {result.latency_ms} ms</Text>
        )}
      </Space>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function DatabaseConnections() {
  const [connections, setConnections] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState(null)

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState(null)

  const [testingId, setTestingId] = useState(null)
  const [testResult, setTestResult] = useState(null)
  const [testModalOpen, setTestModalOpen] = useState(false)

  const fetchConnections = async () => {
    setLoading(true)
    try {
      const params = { page, page_size: pageSize }
      if (search) params.search = search
      if (filterType) params.database_type = filterType
      const res = await dbConnectionAPI.list(params)
      setConnections(res.data.items)
      setTotal(res.data.total)
    } catch {
      message.error('Failed to load database connections.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, filterType])

  const handleDelete = async (id) => {
    try {
      await dbConnectionAPI.delete(id)
      message.success('Connection deleted.')
      fetchConnections()
    } catch {
      message.error('Failed to delete connection.')
    }
  }

  const handleSetActive = async (connection) => {
    if (connection.is_active) return // already active
    try {
      await dbConnectionAPI.activate(connection.id, true)
      message.success(`"${connection.connection_name}" set as active connection. All others deactivated.`)
      fetchConnections()
    } catch {
      message.error('Failed to set active connection.')
    }
  }

  const handleTest = async (id) => {
    setTestingId(id)
    try {
      const res = await dbConnectionAPI.test(id)
      setTestResult(res.data)
      setTestModalOpen(true)
    } catch {
      message.error('Failed to run connection test.')
    } finally {
      setTestingId(null)
    }
  }

  const columns = [
    {
      title: 'Name',
      dataIndex: 'connection_name',
      key: 'connection_name',
      render: (name) => (
        <Space>
          <DatabaseOutlined />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'database_type',
      key: 'database_type',
      width: 120,
      render: (type) => (
        <Tag color={DB_TYPE_COLORS[type] || 'default'}>{type}</Tag>
      ),
    },
    {
      title: 'Host',
      key: 'host',
      render: (_, row) => (
        <Text code>
          {row.host}:{row.port}
        </Text>
      ),
    },
    {
      title: 'Service / DB',
      dataIndex: 'service_name',
      key: 'service_name',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (active) =>
        active ? (
          <Badge status="success" text="Active" />
        ) : (
          <Badge status="default" text="Inactive" />
        ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 180,
      render: (_, row) => (
        <Space size="small">
          <Tooltip title="Test Connection">
            <Button
              size="small"
              icon={
                testingId === row.id ? (
                  <LoadingOutlined />
                ) : (
                  <ThunderboltOutlined />
                )
              }
              onClick={() => handleTest(row.id)}
              disabled={!!testingId}
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                setEditing(row)
                setFormOpen(true)
              }}
            />
          </Tooltip>
          <Tooltip title={row.is_active ? 'Currently active connection' : 'Set as active connection'}>
            <Button
              size="small"
              type={row.is_active ? 'primary' : 'default'}
              disabled={row.is_active}
              style={row.is_active ? { backgroundColor: '#52c41a', borderColor: '#52c41a', color: '#fff' } : {}}
              onClick={() => handleSetActive(row)}
            >
              {row.is_active ? 'Active' : 'Set Active'}
            </Button>
          </Tooltip>
          <Popconfirm
            title="Delete this connection?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(row.id)}
            okText="Delete"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="Delete">
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        {/* Header */}
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <DatabaseOutlined style={{ fontSize: 24 }} />
              <Title level={4} style={{ margin: 0 }}>
                Database Connections
              </Title>
            </Space>
            <div style={{ marginTop: 4 }}>
              <Text type="secondary">
                Manage external database connections for reconciliation, reporting, and
                fraud monitoring.
              </Text>
            </div>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEditing(null)
                setFormOpen(true)
              }}
            >
              Add Connection
            </Button>
          </Col>
        </Row>

        {/* Filters */}
        <Card size="small">
          <Row gutter={12} align="middle">
            <Col flex="auto">
              <Input.Search
                placeholder="Search by name, host, or description..."
                allowClear
                enterButton="Search"
                onSearch={(v) => {
                  setSearch(v)
                  setPage(1)
                }}
                style={{ width: 360 }}
              />
            </Col>
            <Col>
              <Select
                placeholder="All Types"
                allowClear
                style={{ width: 150 }}
                onChange={(v) => {
                  setFilterType(v || null)
                  setPage(1)
                }}
              >
                <Option value="ORACLE">Oracle</Option>
                <Option value="POSTGRESQL">PostgreSQL</Option>
              </Select>
            </Col>
            <Col>
              <Button icon={<ReloadOutlined />} onClick={fetchConnections}>
                Refresh
              </Button>
            </Col>
          </Row>
        </Card>

        {/* Table */}
        <Card>
          <Table
            dataSource={connections}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize,
              total,
              showTotal: (t) => `${t} connections`,
              onChange: (p) => setPage(p),
            }}
            locale={{ emptyText: 'No database connections found.' }}
          />
        </Card>
      </Space>

      {/* Add / Edit Modal */}
      <ConnectionFormModal
        open={formOpen}
        connection={editing}
        onSuccess={() => {
          setFormOpen(false)
          setEditing(null)
          fetchConnections()
        }}
        onCancel={() => {
          setFormOpen(false)
          setEditing(null)
        }}
      />

      {/* Test Result Modal */}
      <TestResultModal
        open={testModalOpen}
        result={testResult}
        onClose={() => {
          setTestModalOpen(false)
          setTestResult(null)
        }}
      />
    </div>
  )
}
