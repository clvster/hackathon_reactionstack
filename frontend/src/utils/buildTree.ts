import type { Department } from '../api/departments';

export interface TreeNode {
  key: string;
  title: string;
  children: TreeNode[];
}

export function buildTree(items: Department[], parentId: number | null = null): TreeNode[] {
  return items
    .filter((item) => item.parent_id === parentId)
    .map((item) => ({
      key: String(item.id),
      title: item.name,
      children: buildTree(items, item.id),
    }));
}