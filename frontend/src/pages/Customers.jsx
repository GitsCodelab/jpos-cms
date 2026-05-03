import React, { useState, useCallback, useEffect } from 'react'
import {
  Card,
  Input,
  Button,
  Select,
  Space,
  Table,
  Tag,
  Typography,
  Alert,
  Spin,
  Pagination,
  Row,
  Col,
  Tooltip,
  Modal,
} from 'antd'
import { SearchOutlined, UserOutlined, ExpandOutlined, CompressOutlined } from '@ant-design/icons'
import customerAPI from '../services/customerApi'
import CustomerDetail from './CustomerDetail'

const { Title, Text } = Typography
const { Option } = Select

const STATUS_COLORS = {
  ACTIVE: 'green',
  INACTIVE: 'default',
  BLOCKED: 'red',
  SUSPENDED: 'orange',
}

export default function Customers() {
  const [q, setQ] = useState('')
  const [nationalId, setNationalId] = useState('')
  const [statusFilter, setStatusFilter] = useState(undefined)
  const [segmentFilter, setSegmentFilter] = useState(undefined)

  const [results, setResults] = useState([])
  const [total, setTotal] = useState(null)
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 100

  const [modalCustomerId, setModalCustomerId] = useState(null)
  const [modalMaximized, setModalMaximized] = useState(true)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [noConnection, setNoConnection] = useState(false)
  const [searched, setSearched] = useState(false)

  const runSearch = useCallback(async (currentPage = 1) => {
    const trimQ = q.trim()
    const trimNID = nationalId.trim()

    setLoading(true)
    setError(null)
    setNoConnection(false)
    setSearched(true)

    try {
      const params = {
        page: currentPage,
        page_size: PAGE_SIZE,
      }
      if (trimQ) params.q = trimQ
      if (trimNID) params.national_id = trimNID
      if (statusFilter) params.status = statusFilter
      if (segmentFilter) params.segment = segmentFilter

      const res = await customerAPI.search(params)
      setResults(res.data.items)
      setTotal(res.data.total)
      setPage(currentPage)
    } catch (err) {
      if (err?.response?.status === 503) {
        setNoConnection(true)
        setResults([])
        setTotal(null)
      } else if (err?.response?.status === 400) {
        setError(err.response.data.detail || 'Invalid search input.')
        setResults([])
      } else {
        setError('An unexpected error occurred. Please try again.')
        setResults([])
      }
    } finally {
      setLoading(false)
    }
  }, [q, nationalId, statusFilter, segmentFilter])

  // Auto-load first 100 customers when the page mounts
  useEffect(() => { runSearch(1) }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearch = () => runSearch(1)
  const handlePageChange = (newPage) => runSearch(newPage)
  const handleKeyDown = (e) => { if (e.key === 'Enter') handleSearch() }

  const columns = [
    {
      title: 'Name',
      key: 'name',
      render: (_, row) => (
        <Space>
          <UserOutlined style={{ color: '#8c8c8c' }} />
          <Text strong>{[row.first_name, row.last_name].filter(Boolean).join(' ') || '—'}</Text>
        </Space>
      ),
    },
    {
      title: 'National ID',
      dataIndex: 'national_id',
      render: (v) => v || '—',
    },
    {
      title: 'Mobile',
      dataIndex: 'mobile',
      render: (v) => v || '—',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      render: (v) => v || '—',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      render: (v) => v ? <Tag color={STATUS_COLORS[v] || 'default'}>{v}</Tag> : '—',
    },
    {
      title: 'Segment',
      dataIndex: 'segment',
      render: (v) => v ? <Tag>{v}</Tag> : '—',
    },
    {
      title: 'Branch',
      dataIndex: 'branch_id',
      render: (v) => v || '—',
    },
    {
      title: '',
      key: 'actions',
      width: 56,
      render: (_, row) => (
        <Tooltip title="Open detail">
          <Button
            type="link"
            icon={<ExpandOutlined />}
            onClick={(e) => { e.stopPropagation(); setModalCustomerId(row.id) }}
          />
        </Tooltip>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Title level={3} style={{ marginBottom: 4 }}>Customer Search</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        Showing {PAGE_SIZE} customers. Use the filters below to narrow results.
      </Text>

      {noConnection && (
        <Alert
          type="warning"
          showIcon
          message="No active database connection"
          description="Please activate a database connection in Configuration → Database Connections before searching."
          style={{ marginBottom: 24 }}
        />
      )}

      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Input
              prefix={<SearchOutlined />}
              placeholder="Name / mobile / email / national ID"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={handleKeyDown}
              allowClear
            />
          </Col>
          <Col xs={24} md={6}>
            <Input
              placeholder="Exact national ID"
              value={nationalId}
              onChange={(e) => setNationalId(e.target.value)}
              onKeyDown={handleKeyDown}
              allowClear
            />
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="Status"
              value={statusFilter}
              onChange={setStatusFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value="ACTIVE">Active</Option>
              <Option value="INACTIVE">Inactive</Option>
              <Option value="BLOCKED">Blocked</Option>
              <Option value="SUSPENDED">Suspended</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="Segment"
              value={segmentFilter}
              onChange={setSegmentFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value="RETAIL">Retail</Option>
              <Option value="CORPORATE">Corporate</Option>
              <Option value="VIP">VIP</Option>
              <Option value="SME">SME</Option>
            </Select>
          </Col>
          <Col xs={24} md={2}>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
              style={{ width: '100%' }}
            >
              Search
            </Button>
          </Col>
        </Row>
        {error && (
          <Alert
            type="error"
            message={error}
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      {searched && !noConnection && (
        <Card>
          {total !== null && (
            <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
              {total === 0 ? 'No customers found.' : `Found ${total.toLocaleString()} customer(s).`}
            </Text>
          )}
          <Spin spinning={loading}>
            <Table
              dataSource={results}
              columns={columns}
              rowKey="id"
              pagination={false}
              locale={{ emptyText: loading ? 'Searching…' : 'No results' }}
              onRow={(row) => ({
                style: { cursor: 'pointer' },
                onClick: () => setModalCustomerId(row.id),
              })}
            />
          </Spin>
          {total !== null && total > PAGE_SIZE && (
            <div style={{ marginTop: 16, textAlign: 'right' }}>
              <Pagination
                current={page}
                pageSize={PAGE_SIZE}
                total={total}
                onChange={handlePageChange}
                showSizeChanger={false}
              />
            </div>
          )}
        </Card>
      )}

      <Modal
        open={!!modalCustomerId}
        onCancel={() => setModalCustomerId(null)}
        footer={null}
        width={modalMaximized ? '98%' : '80%'}
        style={{ top: modalMaximized ? 4 : 40 }}
        styles={{
          body: {
            padding: '0 16px 16px',
            maxHeight: modalMaximized ? 'calc(100vh - 112px)' : '72vh',
            overflowY: 'auto',
          },
        }}
        title={
          <Space>
            <UserOutlined style={{ color: '#8c8c8c' }} />
            <span>Customer Detail</span>
            <Button
              size="small"
              type="text"
              icon={modalMaximized ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setModalMaximized((v) => !v)}
              title={modalMaximized ? 'Restore' : 'Maximize'}
            />
          </Space>
        }
        destroyOnClose
      >
        {modalCustomerId && (
          <CustomerDetail customerId={modalCustomerId} isModal />
        )}
      </Modal>
    </div>
  )
}
