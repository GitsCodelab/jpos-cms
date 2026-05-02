import React from 'react'
import { Card, Space, Tag, Typography } from 'antd'
import { BuildOutlined } from '@ant-design/icons'
import { useLocation } from 'react-router-dom'

const { Title, Text } = Typography

/**
 * Converts a URL path to a human-readable page title.
 * e.g. '/acquiring/dispute-operations' → 'Acquiring › Dispute Operations'
 */
const pathToTitle = (pathname) => {
  return pathname
    .split('/')
    .filter(Boolean)
    .map((segment) =>
      segment
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' '),
    )
    .join(' › ')
}

export default function PlaceholderPage() {
  const { pathname } = useLocation()
  const title = pathToTitle(pathname)

  return (
    <div style={{ padding: 24 }}>
      <Card
        style={{ borderColor: '#d8dce6' }}
        bodyStyle={{ padding: '48px 24px' }}
      >
        <Space direction="vertical" align="center" style={{ width: '100%' }}>
          <BuildOutlined style={{ fontSize: 52, color: '#d8dce6' }} />
          <Title
            level={4}
            style={{ color: '#73879c', marginTop: 16, marginBottom: 4 }}
          >
            {title}
          </Title>
          <Text type="secondary" style={{ fontSize: 12 }}>
            This section is currently under development.
          </Text>
          <Tag color="blue" style={{ marginTop: 8 }}>
            Coming Soon
          </Tag>
        </Space>
      </Card>
    </div>
  )
}
