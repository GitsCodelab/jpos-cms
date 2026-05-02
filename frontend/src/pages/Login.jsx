import { useState } from 'react'
import { Button, Card, Form, Input, Typography, Space, Alert } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { authAPI } from '../services/api'

const { Title, Text } = Typography

export default function Login({ onLoginSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const onFinish = async (values) => {
    setLoading(true)
    setError('')
    try {
      const response = await authAPI.login(values.username, values.password)
      const { access_token, user } = response.data
      
      // Store token and user info in localStorage
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Call success callback
      onLoginSuccess(user.username)
    } catch (err) {
      const errorMessage = err?.response?.data?.detail || 'Login failed'
      setError(errorMessage)
      console.error('Login error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24 }}>
      <Card style={{ width: '100%', maxWidth: 420 }}>
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Title level={4} style={{ margin: 0 }}>jPOS CMS Login</Title>
          <Text type="secondary">Default credentials: admin / admin123</Text>

          {error && <Alert type="error" message={error} showIcon />}

          <Form
            layout="vertical"
            onFinish={onFinish}
            initialValues={{ username: 'admin', password: 'admin123' }}
          >
            <Form.Item
              label="Username"
              name="username"
              rules={[{ required: true, message: 'Please enter your username' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="Username" />
            </Form.Item>

            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Please enter your password' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Password" />
            </Form.Item>

            <Button type="primary" htmlType="submit" block loading={loading}>
              Sign In
            </Button>
          </Form>
        </Space>
      </Card>
    </div>
  )
}
