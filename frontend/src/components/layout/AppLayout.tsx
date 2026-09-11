import { Layout, Menu } from 'antd';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  ApartmentOutlined,
  TeamOutlined,
  BookOutlined, 
  CalendarOutlined,
  BarChartOutlined,
  LogoutOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const MENU_ITEMS = [
  { key: '/tree', icon: <ApartmentOutlined />, label: 'Структура' },
  { key: '/employees', icon: <TeamOutlined />, label: 'Сотрудники' },
  { key: '/skills', icon: <BookOutlined />, label: 'Навыки' }, 
  { key: '/meetings', icon: <CalendarOutlined />, label: 'Встречи' },
  { key: '/analytics', icon: <BarChartOutlined />, label: 'Аналитика' },
];

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220}>
        <div style={{ color: 'white', textAlign: 'center', padding: 16, fontWeight: 600 }}>
          Performance Review
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={MENU_ITEMS}
          onClick={(e) => navigate(e.key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            padding: '0 24px',
          }}
        >
          <LogoutOutlined
            style={{ fontSize: 18, cursor: 'pointer' }}
            onClick={handleLogout}
          />
        </Header>
        <Content style={{ background: '#f5f5f5' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}