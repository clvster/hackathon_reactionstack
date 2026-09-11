import { useState } from 'react';
import { Tree, Spin } from 'antd';
import type { TreeProps } from 'antd';
import {
  useDepartmentTree,
  flattenTree,
  useUpdateDepartmentParent,
} from '../api/departments';
import { toAntTree } from '../utils/buildTree';
import { usePermissions } from '../api/permissions';
import EmployeeCardModal from '../components/employee/EmployeeCardModal';

export default function OrgTreePage() {
  const { data: tree, isLoading } = useDepartmentTree();
  const { data: permissions } = usePermissions();
  const updateParent = useUpdateDepartmentParent();
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  if (isLoading || !tree) return <Spin />;

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
      <h2>Структура подразделений</h2>
      <Tree
        treeData={toAntTree(tree)}
        defaultExpandAll
        draggable={!!permissions?.is_admin}
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