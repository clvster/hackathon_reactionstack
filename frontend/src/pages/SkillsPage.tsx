import { useState } from 'react';
import { Table, Button, Tabs, Tag, Space, Modal, Form, Input, Select, DatePicker, message } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { SkillBadge } from '../components/ui/SkillBadge';
import { useUsers } from '../api/users';
import { usePermissions } from '../api/permissions';
import {
  useSkills,
  useCreateSkill,
  useUpdateSkill,
  useAddSkillsToPlan,
  useUserPlan,
  type Skill,
  type PlanItem,
} from '../api/skills';
import type { ColumnsType } from 'antd/es/table';

const { Option } = Select;

// TODO: подтвердить точные строковые значения от бэка и подставить сюда
const DIRECTION_LABELS: Record<string, string> = {
  BACK: 'Backend',
  FRONT: 'Frontend',
  QA: 'QA',
};

export const SkillsPage = () => {
  const { data: permissions } = usePermissions();
  const { data: skills, isLoading } = useSkills();
  const { data: users } = useUsers();
  const createSkill = useCreateSkill();
  const updateSkill = useUpdateSkill();
  const addToPlan = useAddSkillsToPlan();

  const [selectedUserId, setSelectedUserId] = useState<number | undefined>(users?.[0]?.id);
  const { data: planItems, isLoading: isPlanLoading } = useUserPlan(selectedUserId);

  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null);
  const [form] = Form.useForm();
  const [planForm] = Form.useForm();

  const selectedUser = users?.find((u) => u.id === selectedUserId);

  const handleAddSkill = () => {
    setEditingSkill(null);
    form.resetFields();
    setIsSkillModalOpen(true);
  };

  const handleEditSkill = (skill: Skill) => {
    setEditingSkill(skill);
    form.setFieldsValue({ name: skill.name, direction_id: skill.direction_id });
    setIsSkillModalOpen(true);
  };

  const handleSkillSubmit = () => {
    form.validateFields().then((values) => {
      if (editingSkill) {
        updateSkill.mutate(
          { id: editingSkill.id, ...values },
          { onSuccess: () => message.success('Навык обновлён') }
        );
      } else {
        createSkill.mutate(values, { onSuccess: () => message.success('Навык добавлен') });
      }
      setIsSkillModalOpen(false);
      form.resetFields();
    });
  };

  const skillColumns: ColumnsType<Skill> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 80, sorter: (a, b) => a.id - b.id },
    { title: 'Название навыка', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
    {
      title: 'Направление',
      dataIndex: 'direction_id',
      key: 'direction_id',
      render: (id: string) => <Tag>{DIRECTION_LABELS[id] ?? id}</Tag>,
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 160,
      render: (_, record) => (
        <Button type="link" icon={<EditOutlined />} onClick={() => handleEditSkill(record)}>
          Редактировать
        </Button>
      ),
    },
  ];

  const handleAddPlanItem = () => {
    if (!selectedUserId) {
      message.error('Сначала выберите сотрудника');
      return;
    }
    planForm.resetFields();
    setIsPlanModalOpen(true);
  };

  const handlePlanSubmit = () => {
    planForm.validateFields().then((values) => {
      if (!selectedUserId) return;

      addToPlan.mutate(
        {
          userId: selectedUserId,
          items: [{ skill_id: values.skill_id, target_date: values.target_date.format('YYYY-MM-DD') }],
        },
        {
          onSuccess: () => {
            message.success('Навык добавлен в план');
          },
          onError: () => message.error('Не удалось добавить навык в план'),
        }
      );

      setIsPlanModalOpen(false);
      planForm.resetFields();
    });
  };

  const planColumns: ColumnsType<PlanItem> = [
    { title: 'Навык', dataIndex: ['skill', 'name'], key: 'skill_name' },
    {
      title: 'Направление',
      dataIndex: ['skill', 'direction_id'],
      key: 'direction',
      render: (id: string) => <Tag>{DIRECTION_LABELS[id] ?? id}</Tag>,
    },
    { title: 'Плановая дата', dataIndex: 'target_date', key: 'target_date' },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: PlanItem['status']) => <SkillBadge status={status} />,
    },
    {
      title: 'Дата подтверждения',
      dataIndex: 'confirmed_at',
      key: 'confirmed_at',
      render: (date: string | null) => date || '—',
    },
    {
      title: 'Комментарий',
      dataIndex: 'problem_comment',
      key: 'problem_comment',
      render: (text: string | null) => text || '—',
    },
  ];

  const tabItems = [
    {
      key: 'plan',
      label: 'Годовой план обучения',
      children: (
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 16,
            }}
          >
            <Space>
              <h3 style={{ margin: 0 }}>
                План сотрудника{selectedUser ? `: ${selectedUser.full_name}` : ''}
              </h3>
              <Select
                style={{ width: 260 }}
                value={selectedUserId}
                onChange={setSelectedUserId}
                options={(users ?? []).map((u) => ({ value: u.id, label: u.full_name }))}
                placeholder="Выберите сотрудника"
              />
            </Space>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAddPlanItem}>
              Добавить навык в план
            </Button>
          </div>
          <Table
            columns={planColumns}
            dataSource={planItems}
            rowKey="id"
            loading={isPlanLoading}
            pagination={{ pageSize: 10 }}
          />
        </div>
      ),
    },
    ...(permissions?.is_admin
      ? [
          {
            key: 'skills',
            label: 'Справочник навыков (Админ)',
            children: (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                  <h3>Справочник навыков</h3>
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleAddSkill}>
                    Добавить навык
                  </Button>
                </div>
                <Table
                  columns={skillColumns}
                  dataSource={skills}
                  rowKey="id"
                  loading={isLoading}
                  pagination={{ pageSize: 10 }}
                />
              </div>
            ),
          },
        ]
      : []),
  ];

  return (
    <div style={{ padding: 24 }}>
      <Tabs defaultActiveKey="plan" items={tabItems} />

      <Modal
        title={editingSkill ? 'Редактировать навык' : 'Добавить новый навык'}
        open={isSkillModalOpen}
        onOk={handleSkillSubmit}
        onCancel={() => setIsSkillModalOpen(false)}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="name" label="Название навыка" rules={[{ required: true, message: 'Введите название навыка' }]}>
            <Input placeholder="Например: React Hooks" />
          </Form.Item>
          <Form.Item name="direction_id" label="Направление" rules={[{ required: true, message: 'Выберите направление' }]}>
            <Select placeholder="Выберите направление">
              <Option value="BACK">Backend</Option>
              <Option value="FRONT">Frontend</Option>
              <Option value="QA">QA</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Добавить навык в годовой план"
        open={isPlanModalOpen}
        onOk={handlePlanSubmit}
        onCancel={() => setIsPlanModalOpen(false)}
        okText="Добавить"
        cancelText="Отмена"
      >
        <Form form={planForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="skill_id" label="Навык" rules={[{ required: true, message: 'Выберите навык' }]}>
            <Select placeholder="Выберите навык из справочника">
              {(skills ?? []).map((skill) => (
                <Option key={skill.id} value={skill.id}>
                  {skill.name} ({DIRECTION_LABELS[skill.direction_id] ?? skill.direction_id})
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="target_date" label="Плановая дата подтверждения" rules={[{ required: true, message: 'Выберите дату' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};