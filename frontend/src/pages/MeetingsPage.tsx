import { useState } from 'react';
import { Table, Button, Modal, Form, DatePicker, Select, Input, List } from 'antd';
import ReactMarkdown from 'react-markdown';
import { useMeetings, useCreateMeeting } from '../api/meetings';
import { useUsers } from '../api/users';

export default function MeetingsPage() {
  const { data: meetings, isLoading } = useMeetings();
  const { data: users } = useUsers();
  const createMeeting = useCreateMeeting();
  const [modalOpen, setModalOpen] = useState(false);
  const [previewMeeting, setPreviewMeeting] = useState<number | null>(null);
  const [form] = Form.useForm();

  const columns = [
    { title: 'Дата', dataIndex: 'date', key: 'date' },
    {
      title: 'Участники',
      dataIndex: 'participant_names',
      key: 'participant_names',
      render: (names: string[]) => names.join(', '),
    },
    {
      title: '',
      key: 'actions',
      render: (_: unknown, record: { id: number }) => (
        <Button type="link" onClick={() => setPreviewMeeting(record.id)}>
          Открыть
        </Button>
      ),
    },
  ];

  const onFinish = (values: any) => {
    createMeeting.mutate({
      date: values.date.format('YYYY-MM-DD'),
      participant_ids: values.participant_ids,
      summary_markdown: values.summary_markdown,
      attachments: values.attachments ? values.attachments.split('\n').filter(Boolean) : [],
      skill_marks: [],
    });
    setModalOpen(false);
    form.resetFields();
  };

  const selected = meetings?.find((m) => m.id === previewMeeting);

  return (
    <div style={{ padding: 24 }}>
      <h2>Встречи 1:1</h2>
      <Button type="primary" onClick={() => setModalOpen(true)} style={{ marginBottom: 16 }}>
        Новая встреча
      </Button>
      <Table rowKey="id" columns={columns} dataSource={meetings} loading={isLoading} />

      <Modal
        title="Новая встреча"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="date" label="Дата" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="participant_ids" label="Участники" rules={[{ required: true }]}>
            <Select
              mode="multiple"
              options={(users ?? []).map((u) => ({ value: u.id, label: u.full_name }))}
            />
          </Form.Item>
          <Form.Item name="summary_markdown" label="Итоги (markdown)" rules={[{ required: true }]}>
            <Input.TextArea rows={5} />
          </Form.Item>
          <Form.Item name="attachments" label="Файлы/ссылки (по одной на строку)">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Протокол встречи"
        open={previewMeeting !== null}
        onCancel={() => setPreviewMeeting(null)}
        footer={null}
        width={600}
      >
        {selected && (
          <>
            <ReactMarkdown>{selected.summary_markdown}</ReactMarkdown>
            {selected.attachments.length > 0 && (
              <List
                header="Вложения"
                dataSource={selected.attachments}
                renderItem={(url) => (
                  <List.Item>
                    <a href={url} target="_blank" rel="noreferrer">{url}</a>
                  </List.Item>
                )}
              />
            )}
          </>
        )}
      </Modal>
    </div>
  );
}