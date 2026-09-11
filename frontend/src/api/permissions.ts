import { useQuery } from '@tanstack/react-query';
import { client } from './client';

export interface CurrentUserPermissions {
  user_id: number;
  is_admin: boolean;
  visible_department_ids: number[];
  visible_user_ids: number[];
}

export function usePermissions() {
  return useQuery({
    queryKey: ['permissions', 'me'],
    queryFn: async () => {
      const { data } = await client.get<CurrentUserPermissions>('/permissions/me');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}