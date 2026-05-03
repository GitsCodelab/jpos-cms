import React, { useEffect, useState } from 'react'
import {
  Drawer,
  Descriptions,
  Tag,
  Tabs,
  Spin,
  Alert,
  Typography,
  Space,
  Button,
  Modal,
} from 'antd'
import {
  UserOutlined,
  ExpandOutlined,
  CompressOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import customerAPI from '../../services/customerApi'
import ContractsTab from './tabs/ContractsTab'
import CardsTab from './tabs/CardsTab'
import AccountsTab from './tabs/AccountsTab'
import CustomerDetail from '../../pages/CustomerDetail'

const { Text } = Typography

const STATUS_COLORS = {
  ACTIVE: 'green',
  INACTIVE: 'default',
  BLOCKED: 'red',
  SUSPENDED: 'orange',
}

export default function CustomerDrawer({ customerId, onClose }) {
  const navigate = useNavigate()
  const [customer, setCustomer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [fullPageOpen, setFullPageOpen] = useState(false)
  const [maximized, setMaximized] = useState(true)

  useEffect(() => {
    if (!customerId) return
    setLoading(true)
    setError(null)
    setCustomer(null)
    customerAPI.getById(customerId)
      .then((res) => setCustomer(res.data))
      .catch((err) => {
        if (err?.response?.status === 404) setError('Customer not found.')
        else setError('Failed to load customer details.')
      })
      .finally(() => setLoading(false))
  }, [customerId])

  const fullName = customer
    ? [customer.first_name, customer.last_name].filter(Boolean).join(' ')
    : '...'

  const tabItems = [
    { key: 'contracts', label: 'Contracts', children: <ContractsTab customerId={customerId} /> },
    { key: 'cards',     label: 'Cards',     children: <CardsTab customerId={customerId} /> },
    { key: 'accounts',  label: 'Accounts',  children: <AccountsTab customerId={customerId} /> },
  ]

  return (
    <Drawer
      open={!!customerId}
      onClose={onClose}
      width={820}
      title={
        <Space>
          <UserOutlined style={{ color: '#8c8c8c' }} />
          <span>{fullName}</span>
          {customer?.status && (
            <Tag color={STATUS_COLORS[customer.status] || 'default'}>{customer.status}</Tag>
          )}
        </Space>
      }
      extra={
        <Button
          size="small"
          icon={<ExpandOutlined />}
          onClick={() => setFullPageOpen(true)}
        >
          Open full page
        </Button>
      }
    >
      {loading && <Spin tip="Loading…" style={{ display: 'block', marginTop: 40 }} />}
      {error && <Alert type="error" message={error} showIcon />}
      {customer && !loading && (
        <>
          <Descriptions bordered size="small" column={2} style={{ marginBottom: 24 }}>
            <Descriptions.Item label="Customer ID">
              <Text copyable>{customer.id}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="National ID">{customer.national_id || '—'}</Descriptions.Item>
            <Descriptions.Item label="Name">{customer.first_name || '—'}</Descriptions.Item>
            <Descriptions.Item label="Segment">
              {customer.segment ? <Tag>{customer.segment}</Tag> : '—'}
            </Descriptions.Item>
            <Descriptions.Item label="Registered">
              {customer.created_at ? new Date(customer.created_at).toLocaleDateString() : '—'}
            </Descriptions.Item>
          </Descriptions>
          <Tabs defaultActiveKey="contracts" items={tabItems} destroyInactiveTabPane={false} />
        </>
      )}

      <Modal
        open={fullPageOpen}
        onCancel={() => setFullPageOpen(false)}
        footer={null}
        width={maximized ? '98%' : '80%'}
        style={{ top: maximized ? 4 : 40 }}
        styles={{
          content: { padding: 0 },
          body: {
            padding: '0 16px 16px',
            maxHeight: maximized ? 'calc(100vh - 112px)' : '72vh',
            overflowY: 'auto',
          },
        }}
        title={
          <Space>
            <UserOutlined style={{ color: '#8c8c8c' }} />
            <span>{fullName}</span>
            <Button
              size="small"
              type="text"
              icon={maximized ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setMaximized((v) => !v)}
              title={maximized ? 'Restore' : 'Maximize'}
            />
          </Space>
        }
        destroyOnClose={false}
      >
        {fullPageOpen && (
          <CustomerDetail customerId={customerId} isModal />
        )}
      </Modal>
    </Drawer>
  )
}
