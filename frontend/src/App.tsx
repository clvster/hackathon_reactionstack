import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import LoginPage from './pages/LoginPage';
import OrgTreePage from './pages/OrgTreePage';
import EmployeesPage from './pages/EmployeesPage';

import  {SkillsPage}  from './pages/SkillsPage';
import  MeetingsPage  from './pages/MeetingsPage';
import  AnalyticsPage  from './pages/AnalyticsPage';

import AppLayout from './components/layout/AppLayout';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={ruRU}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
<<<<<<< HEAD
            <Route path="/tree" element={<OrgTreePage />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/skills" element={<SkillsPage />} />
            <Route path="/meetings" element={<MeetingsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
=======

            <Route element={<AppLayout />}>
              <Route path="/tree" element={<OrgTreePage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/meetings" element={<MeetingsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
            </Route>
>>>>>>> ec55d0c94a21059407c2922b73e4ad97c6688d9d
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;