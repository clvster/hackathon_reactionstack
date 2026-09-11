import { useState } from 'react';
import { Table, Button, Tabs, Tag, Space, Modal, Form, Input, Select, DatePicker, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { MOCK_SKILLS, MOCK_PLAN_ITEMS } from '../mocks/data';
import { SkillBadge } from '../components/ui/SkillBadge';
import type { SkillRead, PlanItemRead, SkillStatusEnum } from '../api/types';
import type { ColumnsType } from 'antd/es/table';

const { Option } = Select;

export const SkillsPage = () => {
  const [skills, setSkills] = useState<SkillRead[]>(MOCK_SKILLS);
  const [planItems, setPlanItems] = useState<PlanItemRead[]>(MOCK_PLAN_ITEMS);
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<SkillRead | null>(null);
  const [form] = Form.useForm();
  const [planForm] = Form.useForm();


  const handleAddSkill = () => {
    setEditingSkill(null);
    form.resetFields();
    setIsSkillModalOpen(true);
  };

  const handleEditSkill = (skill: SkillRead) => {
    setEditingSkill(skill);
    form.setFieldsValue({
      name: skill.name,
      department_id: skill.department_id,
    });
    setIsSkillModalOpen(true);
  };

  const handleDeleteSkill = (skillId: number) => {
    Modal.confirm({
      title: 'Удалить навык?',
      content: 'Это действие нельзя отменить',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk() {
        setSkills(skills.filter(s => s.id !== skillId));
        message.success('Навык удалён');
      },
    });
  };

  const handleSkillSubmit = () => {
    form.validateFields().then(values => {
      if (editingSkill) {
        // Редактирование
        setSkills(skills.map(s => 
          s.id === editingSkill.id 
            ? { ...s, name: values.name, department_id: values.department_id }
            : s
        ));
        message.success('Навык обновлён');
      } else {
        // Создание
        const newSkill: SkillRead = {
          id: Math.max(...skills.map(s => s.id)) + 1,
          name: values.name,
          department_id: values.department_id,
        };
        setSkills([...skills, newSkill]);
        message.success('Навык добавлен');
      }
      setIsSkillModalOpen(false);
      form.resetFields();
    });
  };

  // Колонки для справочника навыков
  const skillColumns: ColumnsType<SkillRead> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id - b.id,
    },
    {
      title: 'Название навыка',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Направление',
      dataIndex: 'department_id',
      key: 'department_id',
      render: (deptId: number) => {
        const colorMap: Record<number, string> = {
          1: 'blue', 2: 'green', 3: 'purple', 4: 'orange'
        };
        return <Tag color={colorMap[deptId] || 'default'}>Отдел #{deptId}</Tag>;
      },
      filters: [
        { text: 'Отдел #1', value: 1 },
        { text: 'Отдел #2', value: 2 },
        { text: 'Отдел #3', value: 3 },
        { text: 'Отдел #4', value: 4 },
      ],
      onFilter: (value, record) => record.department_id === value,
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEditSkill(record)}
          >
            Редактировать
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteSkill(record.id)}
          >
            Удалить
          </Button>
        </Space>
      ),
    },
  ];


  const handleAddPlanItem = () => {
    planForm.resetFields();
    setIsPlanModalOpen(true);
  };

  const handlePlanSubmit = () => {
    planForm.validateFields().then(values => {
      const selectedSkill = skills.find(s => s.id === values.skill_id);
      if (!selectedSkill) {
        message.error('Выберите навык');
        return;
      }

      const newPlanItem: PlanItemRead = {
        id: Math.max(...planItems.map(p => p.id)) + 1,
        skill: selectedSkill,
        target_date: values.target_date.format('YYYY-MM-DD'),
        status: 'PLANNED',
        confirmed_at: null,
        problem_comment: null,
      };

      setPlanItems([...planItems, newPlanItem]);
      message.success('Навык добавлен в план');
      setIsPlanModalOpen(false);
      planForm.resetFields();
    });
  };

  // Колонки для годового плана
  const planColumns: ColumnsType<PlanItemRead> = [
    {
      title: 'Навык',
      dataIndex: ['skill', 'name'],
      key: 'skill_name',
      sorter: (a, b) => a.skill.name.localeCompare(b.skill.name),
    },
    {
      title: 'Направление',
      dataIndex: ['skill', 'department_id'],
      key: 'direction',
      render: (deptId: number) => {
        const colorMap: Record<number, string> = {
          1: 'blue', 2: 'green', 3: 'purple', 4: 'orange'
        };
        return <Tag color={colorMap[deptId] || 'default'}>Отдел #{deptId}</Tag>;
      },
      filters: [
        { text: 'Отдел #1', value: 1 },
        { text: 'Отдел #2', value: 2 },
        { text: 'Отдел #3', value: 3 },
        { text: 'Отдел #4', value: 4 },
      ],
      onFilter: (value, record) => record.skill.department_id === value,
    },
    {
      title: 'Плановая дата',
      dataIndex: 'target_date',
      key: 'target_date',
      sorter: (a, b) => a.target_date.localeCompare(b.target_date),
      render: (date: string) => {
        const isOverdue = new Date(date) < new Date();
        return (
          <span style={{ color: isOverdue ? '#ff4d4f' : 'inherit' }}>
            {date}
            {isOverdue && ' ⚠️'}
          </span>
        );
      },
    },
    {
        title: 'Статус',
        dataIndex: 'status',
        key: 'status',
        render: (status: SkillStatusEnum) => <SkillBadge status={status} />,
      filters: [
        { text: 'Запланирован', value: 'PLANNED' },
        { text: 'В процессе', value: 'IN TRAINING' },
        { text: 'Зачтён', value: 'CONFIRMED' },
        { text: 'Проблема', value: 'PROBLEM' },
      ],
      onFilter: (value, record) => record.status === value,
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
      ellipsis: true,
    },
  ];


  const tabItems = [
    {
      key: 'plan',
      label: 'Годовой план обучения',
      children: (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3>План сотрудника (Кузнецова Анна)</h3>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={handleAddPlanItem}
            >
              Добавить навык в план
            </Button>
          </div>
          <Table 
            columns={planColumns} 
            dataSource={planItems} 
            rowKey="id" 
            pagination={{ pageSize: 10 }}
          />
        </div>
      ),
    },
    {
      key: 'skills',
      label: 'Справочник навыков (Админ)',
      children: (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3>Справочник навыков</h3>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={handleAddSkill}
            >
              Добавить навык
            </Button>
          </div>
          <Table 
            columns={skillColumns} 
            dataSource={skills} 
            rowKey="id" 
            pagination={{ pageSize: 10 }}
          />
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Tabs defaultActiveKey="plan" items={tabItems} />

      {/* Модальное окно для создания/редактирования навыка */}
      <Modal
        title={editingSkill ? 'Редактировать навык' : 'Добавить новый навык'}
        open={isSkillModalOpen}
        onOk={handleSkillSubmit}
        onCancel={() => setIsSkillModalOpen(false)}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="name"
            label="Название навыка"
            rules={[{ required: true, message: 'Введите название навыка' }]}
          >
            <Input placeholder="Например: React Hooks" />
          </Form.Item>
          <Form.Item
            name="department_id"
            label="Подразделение"
            rules={[{ required: true, message: 'Выберите подразделение' }]}
          >
            <Select placeholder="Выберите подразделение">
              <Option value={1}>Отдел #1 (Frontend)</Option>
              <Option value={2}>Отдел #2 (Backend)</Option>
              <Option value={3}>Отдел #3 (QA)</Option>
              <Option value={4}>Отдел #4 (DevOps)</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Модальное окно для добавления навыка в план */}
      <Modal
        title="Добавить навык в годовой план"
        open={isPlanModalOpen}
        onOk={handlePlanSubmit}
        onCancel={() => setIsPlanModalOpen(false)}
        okText="Добавить"
        cancelText="Отмена"
      >
        <Form form={planForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="skill_id"
            label="Навык"
            rules={[{ required: true, message: 'Выберите навык' }]}
          >
            <Select placeholder="Выберите навык из справочника">
              {skills.map(skill => (
                <Option key={skill.id} value={skill.id}>
                  {skill.name} (Отдел #{skill.department_id})
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="target_date"
            label="Плановая дата подтверждения"
            rules={[{ required: true, message: 'Выберите дату' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};