import { useState } from 'react';
import { Select, Card, Row, Col, Statistic } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useUserAnalytics, useDepartmentAnalytics } from '../api/analytics';
import { useDepartmentTree, flattenTree } from '../api/departments';
import { useUsers } from '../api/users';

export default function AnalyticsPage() {
  const { data: tree } = useDepartmentTree();
  const { data: users } = useUsers();
  const departments = tree ? flattenTree(tree) : [];

  const [departmentId, setDepartmentId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const { data: deptData } = useDepartmentAnalytics(departmentId);
  const { data: userData } = useUserAnalytics(userId);

  return (
    <div style={{ padding: 24 }}>
      <h2>Аналитика</h2>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="По подразделению">
            <Select
              placeholder="Выберите подразделение"
              style={{ width: '100%', marginBottom: 16 }}
              options={departments.map((d) => ({ value: d.id, label: d.name }))}
              onChange={setDepartmentId}
            />
            {deptData && (
              <Row gutter={16}>
                <Col span={8}><Statistic title="Выполнение плана" value={deptData.completion_rate} suffix="%" /></Col>
                <Col span={8}><Statistic title="Проблемы" value={deptData.open_problems_count} /></Col>
                <Col span={8}><Statistic title="Всего в планах" value={deptData.total_planned_skills} /></Col>
              </Row>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="По сотруднику">
            <Select
              placeholder="Выберите сотрудника"
              style={{ width: '100%', marginBottom: 16 }}
              options={(users ?? []).map((u) => ({ value: u.id, label: u.full_name }))}
              onChange={setUserId}
            />
            {userData && (
              <>
                <Statistic title="Просрочено скиллов" value={userData.overdue_skills_count} style={{ marginBottom: 16 }} />
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={userData.monthly_dynamics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#FF5C00" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}