import { Modal, Descriptions, Spin } from 'antd';
import { useUser, useUsers } from '../../api/users';
import { useDepartmentTree, flattenTree } from '../../api/departments';

interface EmployeeCardModalProps {
  userId: number | null;
  open: boolean;
  onClose: () => void;
}

export default function EmployeeCardModal({ userId, open, onClose }: EmployeeCardModalProps) {
  const { data: user, isLoading } = useUser(userId);
  const { data: tree } = useDepartmentTree();
  const { data: users } = useUsers();

  const departments = tree ? flattenTree(tree) : [];
  const department = departments.find((d) => d.id === user?.department_id);
  const leader = users?.find((u) => u.id === department?.leader_id);

  return (
    <Modal title="Профиль сотрудника" open={open} onCancel={onClose} footer={null}>
      {isLoading ? (
        <Spin />
      ) : user ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="ФИО">{user.full_name}</Descriptions.Item>
          <Descriptions.Item label="Направление">{user.direction}</Descriptions.Item>
          <Descriptions.Item label="Подразделение">{department?.name ?? '—'}</Descriptions.Item>
          <Descriptions.Item label="Руководитель">{leader?.full_name ?? '—'}</Descriptions.Item>
        </Descriptions>
      ) : (
        <p>Сотрудник не найден</p>
      )}
    </Modal>
  );
}