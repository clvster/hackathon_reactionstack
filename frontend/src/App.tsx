import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import LoginPage from './pages/LoginPage';
import OrgTreePage from './pages/OrgTreePage';
import EmployeesPage from './pages/EmployeesPage';
import MeetingsPage from './pages/MeetingsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AppLayout from './components/layout/AppLayout';
import {SkillsPage } from './pages/SkillsPage';

const queryClient = new QueryClient();

const theme = {
  token: {
    colorPrimary: '#FF5C00',      // фирменный оранжевый
    colorLink: '#FF5C00',
    colorText: '#1A1A1A',
    colorTextSecondary: '#5C5C5C',
    colorBgLayout: '#F7F7F7',
    borderRadius: 6,
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
  },
  components: {
    Menu: {
      darkItemSelectedBg: '#FF5C00',
      darkItemBg: '#1A1A1A',
      darkSubMenuItemBg: '#1A1A1A',
    },
    Layout: {
      siderBg: '#1A1A1A',
      headerBg: '#FFFFFF',
    },
    Button: {
      colorPrimary: '#FF5C00',
      colorPrimaryHover: '#E05200',
    },
  },
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={ruRU} theme={theme}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route element={<AppLayout />}>
              <Route path="/tree" element={<OrgTreePage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/meetings" element={<MeetingsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/skills" element={<SkillsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;