import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { client } from './client';

export interface DepartmentTreeNode {
  id: number;
  name: string;
  parent_id: number | null;
  leader_id: number | null;
  children: DepartmentTreeNode[];
}

export function useDepartmentTree() {
  return useQuery({
    queryKey: ['departments', 'my-tree'],
    queryFn: async () => {
      const { data } = await client.get<DepartmentTreeNode[]>('/departments/my-tree');
      return data;
    },
  });
}

// разворачиваем дерево в плоский список 
export function flattenTree(nodes: DepartmentTreeNode[]): Omit<DepartmentTreeNode, 'children'>[] {
  const result: Omit<DepartmentTreeNode, 'children'>[] = [];
  const walk = (list: DepartmentTreeNode[]) => {
    for (const node of list) {
      const { children, ...rest } = node;
      result.push(rest);
      if (children.length) walk(children);
    }
  };
  walk(nodes);
  return result;
}

export function useUpdateDepartmentParent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, parent_id }: { id: number; parent_id: number | null }) => {
      const { data } = await client.patch(`/departments/${id}`, { parent_id });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}
export interface Department {
  id: number;
  name: string;
  parent_id: number | null;
  leader_id: number | null;
}