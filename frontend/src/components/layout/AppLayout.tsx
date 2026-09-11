import { Layout, Menu } from 'antd';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  ApartmentOutlined,
  TeamOutlined,
  CalendarOutlined,
  BarChartOutlined,
  ToolOutlined,
  LogoutOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const MENU_ITEMS = [
  { key: '/tree', icon: <ApartmentOutlined />, label: 'Структура' },
  { key: '/employees', icon: <TeamOutlined />, label: 'Сотрудники' },
  { key: '/meetings', icon: <CalendarOutlined />, label: 'Встречи' },
  { key: '/skills', icon: <ToolOutlined />, label: 'Навыки' },
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
    <Layout style={{ minHeight: '100vh', width: '100%'  }}>
      <Sider width={220} style={{ background: '#1A1A1A' }}>
        <div
          style={{
            color: '#FF5C00',
            textAlign: 'left',
            padding: '20px 24px',
            fontWeight: 800,
            fontSize: 20,
            letterSpacing: 0.5,
          }}
        >
          ‹performance›
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={MENU_ITEMS}
          onClick={(e) => navigate(e.key)}
          style={{ background: '#1A1A1A' }}
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
            borderBottom: '1px solid #eee',
          }}
        >
          <LogoutOutlined
            style={{ fontSize: 18, cursor: 'pointer', color: '#1A1A1A' }}
            onClick={handleLogout}
          />
        </Header>
        <Content style={{ background: '#F7F7F7' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}