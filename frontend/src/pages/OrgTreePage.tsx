import { useState, useEffect } from 'react';
import { Tree, Spin } from 'antd';
import type { TreeProps } from 'antd';
import { useDepartments, type Department } from '../api/departments';
import { buildTree } from '../utils/buildTree';
import EmployeeCardModal from '../components/employee/EmployeeCardModal';

export default function OrgTreePage() {
  const { data: departments, isLoading } = useDepartments();
  const [items, setItems] = useState<Department[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (departments) setItems(departments);
  }, [departments]);

  if (isLoading) return <Spin />;

  const onDrop: TreeProps['onDrop'] = (info) => {
    const dragId = Number(info.dragNode.key);
    const dropId = Number(info.node.key);
    const dropToGap = info.dropToGap;

    setItems((prev) =>
      prev.map((item) => {
        if (item.id !== dragId) return item;
        const targetNode = prev.find((d) => d.id === dropId);
        const newParentId = dropToGap ? targetNode?.parent_id ?? null : dropId;
        return { ...item, parent_id: newParentId };
      })
    );
  };

 const onSelect: TreeProps['onSelect'] = (selectedKeys) => {
  if (selectedKeys.length === 0) return;

  const departmentId = Number(selectedKeys[0]);
  const department = items.find((d) => d.id === departmentId);

  if (department?.leader_id) {
    setSelectedUserId(department.leader_id);
    setModalOpen(true);
  } else {
    console.log('У этого подразделения нет назначенного руководителя');
  }
};

  return (
    <div style={{ padding: 24 }}>
      <h2>Структура подразделений</h2>
      <Tree
        treeData={buildTree(items)}
        defaultExpandAll
        draggable
        blockNode
        onDrop={onDrop}
        onSelect={onSelect}
      />
      <EmployeeCardModal
        userId={selectedUserId}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}