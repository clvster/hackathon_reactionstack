import { useQuery } from '@tanstack/react-query';

export interface User {
  id: number;
  full_name: string;
  direction: 'BACK' | 'FRONT' | 'QA';
  department_id: number;
  department_name: string;
  leader_id: number | null;
  leader_name: string | null;
}

const MOCK_USERS: User[] = [
  { id: 1, full_name: 'Иванов Иван Иванович', direction: 'BACK', department_id: 2, department_name: 'Backend', leader_id: null, leader_name: null },
  { id: 2, full_name: 'Петров Пётр Петрович', direction: 'FRONT', department_id: 3, department_name: 'Frontend', leader_id: 1, leader_name: 'Иванов Иван Иванович' },
  { id: 3, full_name: 'Сидорова Анна Сергеевна', direction: 'QA', department_id: 4, department_name: 'QA', leader_id: 1, leader_name: 'Иванов Иван Иванович' },
  { id: 4, full_name: 'Кузнецов Олег Викторович', direction: 'BACK', department_id: 2, department_name: 'Backend', leader_id: 1, leader_name: 'Иванов Иван Иванович' },
  { id: 5, full_name: 'Смирнова Мария Павловна', direction: 'FRONT', department_id: 3, department_name: 'Frontend', leader_id: 2, leader_name: 'Петров Пётр Петрович' },
];

export function useUser(userId: number | null) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => MOCK_USERS.find((u) => u.id === userId) ?? null,
    enabled: userId !== null,
  });
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => MOCK_USERS,
  });
}