import { useQuery } from '@tanstack/react-query';

export interface CurrentUserPermissions {
  user_id: number;
  is_admin: boolean;
  visible_department_ids: number[];
  visible_user_ids: number[];
}

const MOCK_PERMISSIONS: CurrentUserPermissions = {
  user_id: 1,
  is_admin: false,
  visible_department_ids: [1, 2, 3, 4],
  visible_user_ids: [1, 2, 3, 4, 5],
};

export function usePermissions() {
  return useQuery({
    queryKey: ['permissions', 'me'],
    queryFn: async () => MOCK_PERMISSIONS,
    staleTime: 5 * 60 * 1000,
  });
}