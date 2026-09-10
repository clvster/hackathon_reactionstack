import { Modal, Descriptions, Spin } from 'antd';
import { useUser } from '../../api/users';

interface EmployeeCardModalProps {
  userId: number | null;
  open: boolean;
  onClose: () => void;
}

export default function EmployeeCardModal({ userId, open, onClose }: EmployeeCardModalProps) {
  const { data: user, isLoading } = useUser(userId);

  return (
    <Modal
      title="Профиль сотрудника"
      open={open}
      onCancel={onClose}
      footer={null}
    >
      {isLoading ? (
        <Spin />
      ) : user ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="ФИО">{user.full_name}</Descriptions.Item>
          <Descriptions.Item label="Направление">{user.direction}</Descriptions.Item>
          <Descriptions.Item label="Подразделение">{user.department_name}</Descriptions.Item>
          <Descriptions.Item label="Руководитель">
            {user.leader_name ?? '—'}
          </Descriptions.Item>
        </Descriptions>
      ) : (
        <p>Сотрудник не найден</p>
      )}
    </Modal>
  );
}