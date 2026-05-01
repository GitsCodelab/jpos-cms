import { useEffect, useState } from 'react'
import { Layout, Button, Card, Typography, Tag, Space, Divider } from 'antd'
import { ApiOutlined, CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined, LogoutOutlined } from '@ant-design/icons'
import api from './services/api'
import Login from './pages/Login'

const { Header, Content } = Layout
const { Title, Text, Paragraph } = Typography

export default function App() {
  const [username, setUsername] = useState(localStorage.getItem('username'))
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'))
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const handleAutoLogout = () => {
      setIsAuthenticated(false)
      setUsername(null)
      setResult(null)
      setError(null)
    }
    window.addEventListener('auth:logout', handleAutoLogout)
    return () => window.removeEventListener('auth:logout', handleAutoLogout)
  }, [])

  const handleLoginSuccess = (nextUsername) => {
    setUsername(nextUsername)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    setIsAuthenticated(false)
    setUsername(null)
    setResult(null)
    setError(null)
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

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
      <Header style={{ background: '#0a6ed1', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
        <Title level={4} style={{ color: '#fff', margin: 0 }}>jPOS CMS</Title>
        <Space>
          <Tag>{username || 'admin'}</Tag>
          <Button icon={<LogoutOutlined />} onClick={handleLogout}>Logout</Button>
        </Space>
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
