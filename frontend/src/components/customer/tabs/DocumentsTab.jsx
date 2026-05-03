import React, { useEffect, useState } from 'react'
import { Table, Spin, Alert, Empty } from 'antd'
import customerAPI from '../../../services/customerApi'

export default function DocumentsTab({ customerId }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    customerAPI.getDocuments(customerId)
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load documents.'))
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading) return <Spin style={{ display: 'block', margin: '24px auto' }} />
  if (error) return <Alert type="error" message={error} showIcon />
  if (data.length === 0) return <Empty description="No documents found" />

  const columns = [
    { title: 'Document Type', dataIndex: 'document_type', render: (v) => v || '—' },
    { title: 'Document Number', dataIndex: 'document_number', render: (v) => v || '—' },
    { title: 'Issue Date', dataIndex: 'issue_date', render: (v) => v || '—' },
    { title: 'Expiry Date', dataIndex: 'expiry_date', render: (v) => v || '—' },
  ]

  return <Table dataSource={data} columns={columns} rowKey="id" pagination={false} size="small" />
}
