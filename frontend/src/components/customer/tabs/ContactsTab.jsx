import React, { useEffect, useState } from 'react'
import { Table, Tag, Spin, Alert, Empty } from 'antd'
import { CheckCircleOutlined } from '@ant-design/icons'
import customerAPI from '../../../services/customerApi'

export default function ContactsTab({ customerId }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    customerAPI.getContacts(customerId)
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load contacts.'))
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading) return <Spin style={{ display: 'block', margin: '24px auto' }} />
  if (error) return <Alert type="error" message={error} showIcon />
  if (data.length === 0) return <Empty description="No contacts found" />

  const columns = [
    { title: 'Type', dataIndex: 'contact_type', render: (v) => v ? <Tag>{v}</Tag> : '—' },
    { title: 'Value', dataIndex: 'contact_value', render: (v) => v || '—' },
    {
      title: 'Primary',
      dataIndex: 'is_primary',
      width: 80,
      render: (v) => v ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : null,
    },
  ]

  return <Table dataSource={data} columns={columns} rowKey="id" pagination={false} size="small" />
}
