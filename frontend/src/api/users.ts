import { useQuery } from '@tanstack/react-query';

export interface User {
  id: number;
  full_name: string;
  direction: 'BACK' | 'FRONT' | 'QA';
  department_id: number;
  department_name: string;
  leader_id: number | null;
  leader_name: string | null;
  can_edit_pr?: boolean;
  is_subordinate?: boolean;
}

// Временные моковые данные заменим на реальный запрос, когда бэк поднимется
const MOCK_USERS: User[] = [
  {
    id: 1,
    full_name: 'Иванов Иван Иванович',
    direction: 'BACK',
    department_id: 2,
    department_name: 'Backend',
    leader_id: null,
    leader_name: null,
  },
  {
    id: 2,
    full_name: 'Петров Пётр Петрович',
    direction: 'FRONT',
    department_id: 3,
    department_name: 'Frontend',
    leader_id: 1,
    leader_name: 'Иванов Иван Иванович',
  },
];

export function useUser(userId: number | null) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      return MOCK_USERS.find((u) => u.id === userId) ?? null;
    },
    enabled: userId !== null,
  });
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      return MOCK_USERS;
    },
  });
}