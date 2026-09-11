import { useState } from 'react';
import { Tree, Spin, Tag } from 'antd';
import type { TreeProps } from 'antd';
import {
  ApartmentOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import {
  useDepartmentTree,
  flattenTree,
  useUpdateDepartmentParent,
} from '../api/departments';
import { usePermissions } from '../api/permissions';
import EmployeeCardModal from '../components/employee/EmployeeCardModal';
import type { DepartmentTreeNode } from '../api/departments';

interface AntTreeNode {
  key: string;
  title: React.ReactNode;
  children: AntTreeNode[];
}

function getIcon(depth: number) {
  if (depth === 0) return <ApartmentOutlined style={{ color: '#FF5C00' }} />;
  if (depth === 1) return <TeamOutlined style={{ color: '#5C5C5C' }} />;
  return <UserOutlined style={{ color: '#8C8C8C' }} />;
}

function toStyledTree(nodes: DepartmentTreeNode[], depth = 0): AntTreeNode[] {
  return nodes.map((node) => ({
    key: String(node.id),
    title: (
      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {getIcon(depth)}
        <span style={{ fontWeight: depth === 0 ? 600 : 400 }}>{node.name}</span>
        {node.leader_id && (
          <Tag color="orange" style={{ marginLeft: 8, fontSize: 11 }}>
            Есть руководитель
          </Tag>
        )}
      </span>
    ),
    children: toStyledTree(node.children, depth + 1),
  }));
}

export default function OrgTreePage() {
  const { data: tree, isLoading } = useDepartmentTree();
  const { data: permissions } = usePermissions();
  const updateParent = useUpdateDepartmentParent();
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  if (isLoading || !tree) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  const flatItems = flattenTree(tree);

  const onDrop: TreeProps['onDrop'] = (info) => {
    const dragId = Number(info.dragNode.key);
    const dropId = Number(info.node.key);
    const dropToGap = info.dropToGap;

    const targetNode = flatItems.find((d) => d.id === dropId);
    const newParentId = dropToGap ? targetNode?.parent_id ?? null : dropId;

    updateParent.mutate({ id: dragId, parent_id: newParentId });
  };

  const onSelect: TreeProps['onSelect'] = (selectedKeys) => {
    if (selectedKeys.length === 0) return;
    const departmentId = Number(selectedKeys[0]);
    const department = flatItems.find((d) => d.id === departmentId);

    if (department?.leader_id) {
      setSelectedUserId(department.leader_id);
      setModalOpen(true);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 24 }}>Структура подразделений</h2>
      <div
        style={{
          background: '#fff',
          borderRadius: 8,
          padding: '16px 24px',
          boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        }}
      >
        <Tree
          treeData={toStyledTree(tree)}
          defaultExpandAll
          showLine={{ showLeafIcon: false }}
          draggable={!!permissions?.is_admin}
          blockNode
          onDrop={onDrop}
          onSelect={onSelect}
          style={{ fontSize: 15 }}
        />
      </div>
      <EmployeeCardModal
        userId={selectedUserId}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}