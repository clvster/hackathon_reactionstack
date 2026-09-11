import { useState } from 'react';
import { Table, Select, Space } from 'antd';
import { useUsers, type User } from '../api/users';
import { useDepartmentTree, flattenTree } from '../api/departments';

export default function EmployeesPage() {
  const [directionFilter, setDirectionFilter] = useState<string | undefined>();
  const [departmentFilter, setDepartmentFilter] = useState<number | undefined>();

  const { data: users, isLoading } = useUsers({
    direction: directionFilter,
    department_id: departmentFilter,
  });
  const { data: tree } = useDepartmentTree();
  const departments = tree ? flattenTree(tree) : [];

  const columns = [
    { title: 'ФИО', dataIndex: 'full_name', key: 'full_name' },
    { title: 'Направление', dataIndex: 'direction', key: 'direction' },
    {
      title: 'Подразделение',
      dataIndex: 'department_id',
      key: 'department_id',
      render: (id: number | null) => departments.find((d) => d.id === id)?.name ?? '—',
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
          onChange={setDirectionFilter}
        />
        <Select
          placeholder="Подразделение"
          allowClear
          style={{ width: 200 }}
          options={departments.map((d) => ({ value: d.id, label: d.name }))}
          onChange={setDepartmentFilter}
        />
      </Space>
      <Table<User> rowKey="id" columns={columns} dataSource={users} loading={isLoading} />
    </div>
  );
}