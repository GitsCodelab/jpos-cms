import React, { useEffect, useState } from 'react'
import {
  Card,
  Tabs,
  Descriptions,
  Tag,
  Button,
  Spin,
  Alert,
  Typography,
  Space,
  Breadcrumb,
} from 'antd'
import { ArrowLeftOutlined, UserOutlined } from '@ant-design/icons'
import { useParams, useNavigate, Link } from 'react-router-dom'
import customerAPI from '../services/customerApi'
import ContractsTab from '../components/customer/tabs/ContractsTab'
import CardsTab from '../components/customer/tabs/CardsTab'
import AccountsTab from '../components/customer/tabs/AccountsTab'
import DocumentsTab from '../components/customer/tabs/DocumentsTab'
import ContactsTab from '../components/customer/tabs/ContactsTab'

const { Title, Text } = Typography

const STATUS_COLORS = {
  ACTIVE: 'green',
  INACTIVE: 'default',
  BLOCKED: 'red',
  SUSPENDED: 'orange',
}

export default function CustomerDetail({ customerId: customerIdProp, isModal = false }) {
  const { id: idParam } = useParams()
  const id = customerIdProp || idParam
  const navigate = useNavigate()

  const [customer, setCustomer] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [noConnection, setNoConnection] = useState(false)

  useEffect(() => {
    setLoading(true)
    setError(null)
    setNoConnection(false)

    customerAPI.getById(id)
      .then((res) => setCustomer(res.data))
      .catch((err) => {
        if (err?.response?.status === 503) setNoConnection(true)
        else if (err?.response?.status === 404) setError('Customer not found.')
        else setError('Failed to load customer details.')
      })
      .finally(() => setLoading(false))
  }, [id])

  const fullName = customer
    ? [customer.first_name, customer.last_name].filter(Boolean).join(' ')
    : id

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <Spin tip="Loading customer…" size="large" style={{ display: 'block', marginTop: 80 }} />
      </div>
    )
  }

  if (noConnection) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          type="warning"
          showIcon
          message="No active database connection"
          description="Please activate a database connection in Configuration → Database Connections."
          action={
            <Button size="small" onClick={() => navigate('/customers')}>Back to Search</Button>
          }
        />
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          type="error"
          showIcon
          message={error}
          action={
            <Button size="small" onClick={() => navigate('/customers')}>Back to Search</Button>
          }
        />
      </div>
    )
  }

  const tabItems = [
    {
      key: 'contracts',
      label: 'Contracts',
      children: <ContractsTab customerId={id} />,
    },
    {
      key: 'cards',
      label: 'Cards',
      children: <CardsTab customerId={id} />,
    },
    {
      key: 'accounts',
      label: 'Accounts',
      children: <AccountsTab customerId={id} />,
    },
    {
      key: 'documents',
      label: 'Documents',
      children: <DocumentsTab customerId={id} />,
    },
    {
      key: 'contacts',
      label: 'Contacts',
      children: <ContactsTab customerId={id} />,
    },
  ]

  return (
    <div style={{ padding: isModal ? 0 : 24 }}>
      {!isModal && (
        <Breadcrumb
          style={{ marginBottom: 16 }}
          items={[
            { title: <Link to="/customers">Customer Search</Link> },
            { title: fullName },
          ]}
        />
      )}

      <Space align="center" style={{ marginBottom: 24 }}>
        {!isModal && (
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/customers')}>
            Back
          </Button>
        )}
        <Title level={3} style={{ margin: 0 }}>
          <UserOutlined style={{ marginRight: 8, color: '#8c8c8c' }} />
          {fullName || 'Customer Detail'}
        </Title>
        {customer?.status && (
          <Tag color={STATUS_COLORS[customer.status] || 'default'} style={{ fontSize: 14 }}>
            {customer.status}
          </Tag>
        )}
      </Space>

      <Card style={{ marginBottom: 24 }}>
        <Descriptions bordered size="small" column={{ xs: 1, sm: 2, md: 3 }}>
          <Descriptions.Item label="Customer ID">
            <Text copyable>{customer.id}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="First Name">{customer.first_name || '—'}</Descriptions.Item>
          <Descriptions.Item label="Last Name">{customer.last_name || '—'}</Descriptions.Item>
          <Descriptions.Item label="National ID">{customer.national_id || '—'}</Descriptions.Item>
          <Descriptions.Item label="Mobile">{customer.mobile || '—'}</Descriptions.Item>
          <Descriptions.Item label="Email">{customer.email || '—'}</Descriptions.Item>
          <Descriptions.Item label="Segment">
            {customer.segment ? <Tag>{customer.segment}</Tag> : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Branch">{customer.branch_id || '—'}</Descriptions.Item>
          <Descriptions.Item label="Registered">
            {customer.created_at
              ? new Date(customer.created_at).toLocaleDateString()
              : '—'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card>
        <Tabs defaultActiveKey="contracts" items={tabItems} destroyInactiveTabPane={false} />
      </Card>
    </div>
  )
}
