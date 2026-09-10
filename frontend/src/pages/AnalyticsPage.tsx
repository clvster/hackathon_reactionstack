import { useState } from 'react';
import { Select, Card, Row, Col } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTeamProgress, useUserProgress } from '../api/analytics';
import { useDepartments } from '../api/departments';
import { useUsers } from '../api/users';

export default function AnalyticsPage() {
  const { data: departments } = useDepartments();
  const { data: users } = useUsers();
  const [departmentId, setDepartmentId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const { data: teamData } = useTeamProgress(departmentId);
  const { data: userData } = useUserProgress(userId);

  return (
    <div style={{ padding: 24 }}>
      <h2>Аналитика</h2>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="Прогресс по подразделению">
            <Select
              placeholder="Выберите подразделение"
              style={{ width: '100%', marginBottom: 16 }}
              options={(departments ?? []).map((d) => ({ value: d.id, label: d.name }))}
              onChange={setDepartmentId}
            />
            {teamData && (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={teamData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="progress" stroke="#4f46e5" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Прогресс по сотруднику">
            <Select
              placeholder="Выберите сотрудника"
              style={{ width: '100%', marginBottom: 16 }}
              options={(users ?? []).map((u) => ({ value: u.id, label: u.full_name }))}
              onChange={setUserId}
            />
            {userData && (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={userData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="progress" stroke="#dc2626" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}