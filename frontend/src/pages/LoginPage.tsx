import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, message } from 'antd';
import { useLogin } from '../api/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useLogin();

  const onFinish = (values: { username: string; password: string }) => {
    login.mutate(values, {
      onSuccess: () => navigate('/tree'),
      onError: (error: any) => {
        message.error(error.response?.data?.detail ?? 'Ошибка входа');
      },
    });
  };

  return (
    <div style={{ maxWidth: 320, margin: '100px auto' }}>
      <h2 style={{ color: '#1A1A1A', fontWeight: 800 }}>Вход</h2>

      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="username" required={false} label="Логин" rules={[
          { required: true, message: 'Пожалуйста, введите логин' },
          { min: 2, message: 'Минимум 2 символа' },
          { max: 16, message: 'Максимум 16 символов' },
          { pattern: /^[a-zA-Z0-9@.]+$/, message: 'Только латинские буквы' },
          ]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" required={false} label="Пароль" rules={[
          { required: true, message: 'Пожалуйста, введите пароль' },
          { min: 6, message: 'Минимум 6 символов' },
          { max: 32, message: 'Максимум 32 символа' },
          ]}>
          <Input.Password />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={login.isPending} block>
          Войти
        </Button>
      </Form>

    </div>
  );
}