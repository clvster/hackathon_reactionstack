import { useState, useEffect } from 'react';
import { Tree, Spin } from 'antd';
import type { TreeProps } from 'antd';
import { useDepartments, type Department } from '../api/departments';
import { buildTree } from '../utils/buildTree';

export default function OrgTreePage() {
  const { data: departments, isLoading } = useDepartments();
  const [items, setItems] = useState<Department[]>([]);

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

    // бэк даст эндпоинт  здесь вызвать
    // client.patch(`/departments/${dragId}`, { parent_id: newParentId })
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
      />
    </div>
  );
}