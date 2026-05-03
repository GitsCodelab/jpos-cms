import React, { useEffect, useState } from 'react'
import { Table, Tag, Spin, Alert, Empty } from 'antd'
import customerAPI from '../../../services/customerApi'

const STATUS_COLORS = {
  ACTIVE: 'green',
  CLOSED: 'red',
  SUSPENDED: 'orange',
}

export default function ContractsTab({ customerId }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    customerAPI.getContracts(customerId)
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load contracts.'))
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading) return <Spin style={{ display: 'block', margin: '24px auto' }} />
  if (error) return <Alert type="error" message={error} showIcon />
  if (data.length === 0) return <Empty description="No contracts found" />

  const columns = [
    { title: 'Contract #', dataIndex: 'contract_number', render: (v) => v || '—' },
    {
      title: 'Type',
      key: 'type',
      render: (_, row) => row.contract_type_desc || row.product_type || '—',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      render: (v) => v ? <Tag color={STATUS_COLORS[v] || 'default'}>{v}</Tag> : '—',
    },
    {
      title: 'Open Date',
      dataIndex: 'open_date',
      render: (v) => v ? new Date(v).toLocaleDateString() : '—',
    },
    {
      title: 'Close Date',
      dataIndex: 'close_date',
      render: (v) => v ? new Date(v).toLocaleDateString() : '—',
    },
  ]

  return <Table dataSource={data} columns={columns} rowKey="id" pagination={false} size="small" />
}
