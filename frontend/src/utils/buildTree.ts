import type { DepartmentTreeNode } from '../api/departments';

export interface AntTreeNode {
  key: string;
  title: string;
  children: AntTreeNode[];
}

export function toAntTree(nodes: DepartmentTreeNode[]): AntTreeNode[] {
  return nodes.map((node) => ({
    key: String(node.id),
    title: node.name,
    children: toAntTree(node.children),
  }));
}