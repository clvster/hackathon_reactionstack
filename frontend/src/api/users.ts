import { useQuery } from '@tanstack/react-query';
import { client } from './client';

export type Direction = 'BACK' | 'FRONT' | 'QA';

export interface User {
  id: number;
  username: string;
  email: string | null;
  full_name: string;
  direction: Direction;
  department_id: number | null;
  is_admin: boolean;
}

export function useUsers(filters?: { direction?: string; department_id?: number }) {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: async () => {
      const { data } = await client.get<User[]>('/users', { params: filters });
      return data;
    },
  });
}

export function useUser(userId: number | null) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const { data } = await client.get<User>(`/users/${userId}`);
      return data;
    },
    enabled: userId !== null,
  });
}