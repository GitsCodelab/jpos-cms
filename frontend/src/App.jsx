import { useState } from 'react'
import { Layout, Button, Card, Typography, Tag, Space, Divider } from 'antd'
import { ApiOutlined, CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons'
import api from './services/api'

const { Header, Content } = Layout
const { Title, Text, Paragraph } = Typography

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const testPing = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.get('/ping')
      setResult(res.data)
    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#0a6ed1', display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <Title level={4} style={{ color: '#fff', margin: 0 }}>jPOS CMS</Title>
      </Header>
      <Content style={{ padding: 40 }}>
        <Card
          title={
            <Space>
              <ApiOutlined />
              <span>Backend Integration Test</span>
            </Space>
          }
          style={{ maxWidth: 520 }}
        >
          <Paragraph type="secondary">
            Click the button below to call <Text code>GET /api/ping</Text> on the backend.
          </Paragraph>
          <Button
            type="primary"
            icon={loading ? <LoadingOutlined /> : <ApiOutlined />}
            onClick={testPing}
            loading={loading}
          >
            Ping Backend
          </Button>

          {result && (
            <>
              <Divider />
              <Space direction="vertical" size={4}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#107e3e' }} />
                  <Text strong style={{ color: '#107e3e' }}>Connected</Text>
                </Space>
                <Text>Status: <Tag color="success">{result.status}</Tag></Text>
                <Text>Service: <Tag color="blue">{result.service}</Tag></Text>
                <Text>Version: <Tag>{result.version}</Tag></Text>
              </Space>
            </>
          )}

          {error && (
            <>
              <Divider />
              <Space>
                <CloseCircleOutlined style={{ color: '#bb0000' }} />
                <Text type="danger">{error}</Text>
              </Space>
            </>
          )}
        </Card>
      </Content>
    </Layout>
  )
}
