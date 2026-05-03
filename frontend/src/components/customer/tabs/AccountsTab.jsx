import React, { useEffect, useState } from 'react'
import { Table, Tag, Spin, Alert, Empty, Typography } from 'antd'
import customerAPI from '../../../services/customerApi'

const { Text } = Typography

const STATUS_COLORS = {
  ACTIVE: 'green',
  INACTIVE: 'default',
  CLOSED: 'red',
  FROZEN: 'orange',
}

export default function AccountsTab({ customerId }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    customerAPI.getAccounts(customerId)
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load accounts.'))
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading) return <Spin style={{ display: 'block', margin: '24px auto' }} />
  if (error) return <Alert type="error" message={error} showIcon />
  if (data.length === 0) return <Empty description="No accounts found" />

  const columns = [
    { title: 'Account Number', dataIndex: 'account_number', render: (v) => v || '—' },
    { title: 'Currency', dataIndex: 'currency', render: (v) => v || '—' },
    {
      title: 'Balance',
      dataIndex: 'balance',
      render: (v) =>
        v == null
          ? <Text type="secondary" italic>Restricted</Text>
          : <Text>{Number(v).toLocaleString(undefined, { minimumFractionDigits: 2 })}</Text>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      render: (v) => v ? <Tag color={STATUS_COLORS[v] || 'default'}>{v}</Tag> : '—',
    },
  ]

  return <Table dataSource={data} columns={columns} rowKey="id" pagination={false} size="small" />
}
