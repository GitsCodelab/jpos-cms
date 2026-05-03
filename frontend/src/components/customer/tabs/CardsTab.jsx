import React, { useEffect, useState } from 'react'
import { Table, Tag, Spin, Alert, Empty, Button, Tooltip } from 'antd'
import { CreditCardOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons'
import customerAPI from '../../../services/customerApi'

const STATUS_COLORS = {
  ACTIVE: 'green',
  BLOCKED: 'red',
  EXPIRED: 'default',
  CANCELLED: 'volcano',
}

export default function CardsTab({ customerId }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  // set of row ids currently showing clear PAN
  const [visiblePans, setVisiblePans] = useState(new Set())

  useEffect(() => {
    setLoading(true)
    setVisiblePans(new Set())
    // fetch with include_pan=true so clear PAN is available if user is authorized
    customerAPI.getCards(customerId, { includePan: true })
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load cards.'))
      .finally(() => setLoading(false))
  }, [customerId])

  const togglePan = (id) => {
    setVisiblePans((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  if (loading) return <Spin style={{ display: 'block', margin: '24px auto' }} />
  if (error) return <Alert type="error" message={error} showIcon />
  if (data.length === 0) return <Empty description="No cards found" />

  const columns = [
    {
      title: 'Card Number',
      key: 'card_number',
      render: (_, row) => {
        const panVisible = visiblePans.has(row.id)
        const displayNumber = panVisible
          ? (row.card_number_clear || row.card_number_masked || '—')
          : (row.card_number_masked || '—')
        return (
          <span style={{ fontFamily: 'monospace', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <CreditCardOutlined style={{ color: '#8c8c8c' }} />
            {displayNumber}
            {row.card_number_clear && (
              <Tooltip title={panVisible ? 'Hide PAN' : 'Show full PAN'}>
                <Button
                  type="text"
                  size="small"
                  icon={panVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  style={{ color: panVisible ? '#ff4d4f' : '#8c8c8c', padding: '0 2px' }}
                  onClick={() => togglePan(row.id)}
                />
              </Tooltip>
            )}
          </span>
        )
      },
    },
    { title: 'Type', dataIndex: 'card_type', render: (v) => v || '—' },
    {
      title: 'Status',
      dataIndex: 'status',
      render: (v) => v ? <Tag color={STATUS_COLORS[v] || 'default'}>{v}</Tag> : '—',
    },
    { title: 'Expiry', dataIndex: 'expiry_date', render: (v) => v || '—' },
  ]

  return <Table dataSource={data} columns={columns} rowKey="id" pagination={false} size="small" />
}
