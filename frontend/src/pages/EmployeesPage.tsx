import { useState } from 'react';
import { Table, Select, Space } from 'antd';
import { useUsers, type User } from '../api/users';
import { useDepartments } from '../api/departments';
import { usePermissions } from '../api/permissions';

export default function EmployeesPage() {
  const { data: users, isLoading } = useUsers();
  const { data: departments } = useDepartments();
  const { data: permissions } = usePermissions();

  const [directionFilter, setDirectionFilter] = useState<string | null>(null);
  const [departmentFilter, setDepartmentFilter] = useState<number | null>(null);

  const visibleUsers = (users ?? []).filter(
    (u) => permissions?.is_admin || permissions?.visible_user_ids.includes(u.id)
  );

  const filteredUsers = visibleUsers.filter((u) => {
    if (directionFilter && u.direction !== directionFilter) return false;
    if (departmentFilter && u.department_id !== departmentFilter) return false;
    return true;
  });

  const columns = [
    { title: 'ФИО', dataIndex: 'full_name', key: 'full_name' },
    { title: 'Направление', dataIndex: 'direction', key: 'direction' },
    { title: 'Подразделение', dataIndex: 'department_name', key: 'department_name' },
    {
      title: 'Руководитель',
      dataIndex: 'leader_name',
      key: 'leader_name',
      render: (v: string | null) => v ?? '—',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h2>Сотрудники</h2>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Направление"
          allowClear
          style={{ width: 160 }}
          options={[
            { value: 'BACK', label: 'BACK' },
            { value: 'FRONT', label: 'FRONT' },
            { value: 'QA', label: 'QA' },
          ]}
          onChange={(value) => setDirectionFilter(value ?? null)}
        />
        <Select
          placeholder="Подразделение"
          allowClear
          style={{ width: 200 }}
          options={(departments ?? []).map((d) => ({ value: d.id, label: d.name }))}
          onChange={(value) => setDepartmentFilter(value ?? null)}
        />
      </Space>
      <Table<User>
        rowKey="id"
        columns={columns}
        dataSource={filteredUsers}
        loading={isLoading}
      />
    </div>
  );
}