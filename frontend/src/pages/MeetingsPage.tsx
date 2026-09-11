import { useState } from 'react';
import { Table, Button, Modal, Form, DatePicker, Select, Input } from 'antd';
import ReactMarkdown from 'react-markdown';
import { useMeetings, useCreateMeeting } from '../api/meetings';
import { useUsers } from '../api/users';
import dayjs from 'dayjs';

export default function MeetingsPage() {
  const { data: meetings, isLoading } = useMeetings();
  const { data: users } = useUsers();
  const createMeeting = useCreateMeeting();
  const [modalOpen, setModalOpen] = useState(false);
  const [previewId, setPreviewId] = useState<number | null>(null);
  const [form] = Form.useForm();

  const columns = [
    {
      title: 'Дата',
      dataIndex: 'meeting_date',
      key: 'meeting_date',
      render: (d: string) => dayjs(d).format('DD.MM.YYYY'),
    },
    {
      title: 'Сотрудник',
      dataIndex: 'participant_id',
      key: 'participant_id',
      render: (id: number) => users?.find((u) => u.id === id)?.full_name ?? id,
    },
    {
      title: '',
      key: 'actions',
      render: (_: unknown, record: { id: number }) => (
        <Button type="link" onClick={() => setPreviewId(record.id)}>Открыть</Button>
      ),
    },
  ];

  const onFinish = (values: any) => {
    createMeeting.mutate({
      participant_id: values.participant_id,
      meeting_date: values.meeting_date.toISOString(),
      summary_markdown: values.summary_markdown,
      files_and_links: values.files_and_links
        ? values.files_and_links.split('\n').filter(Boolean)
        : [],
      assessments: [],
      global_problem_comment: values.global_problem_comment || null,
    });
    setModalOpen(false);
    form.resetFields();
    
  };

  const selected = meetings?.find((m) => m.id === previewId);

  return (
    <div style={{ padding: 24 }}>
      <h2>Встречи 1:1</h2>
      <Button type="primary" onClick={() => setModalOpen(true)} style={{ marginBottom: 16 }}>
        Новая встреча
      </Button>
      <Table rowKey="id" columns={columns} dataSource={meetings} loading={isLoading} />

      <Modal title="Записать протокол встречи" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="participant_id" label="Сотрудник" rules={[{ required: true }]}>
            <Select options={(users ?? []).map((u) => ({ value: u.id, label: u.full_name }))} />
          </Form.Item>
          <Form.Item name="meeting_date" label="Дата проведения встречи" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="summary_markdown" label="Итоги встречи (что обсудили, markdown)" rules={[{ required: true, min: 10 }]}>
            <Input.TextArea rows={5} placeholder="Например: обсудили прогресс по FastAPI, договорились..." />
          </Form.Item>
          <Form.Item name="files_and_links" label="Файлы/ссылки (по одной на строку)">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="global_problem_comment" label="Общая проблема (необязательно)">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Протокол встречи" open={previewId !== null} onCancel={() => setPreviewId(null)} footer={null} width={600}>
        {selected && <ReactMarkdown>{selected.summary_markdown}</ReactMarkdown>}
      </Modal>
    </div>
  );
}