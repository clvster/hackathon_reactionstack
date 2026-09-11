import { useQuery } from '@tanstack/react-query';
import { client } from './client';

export interface MonthlyHistoryItem {
  month: string;
  count: number;
}

export interface UserAnalytics {
  user_id: number;
  overdue_skills_count: number;
  monthly_dynamics: MonthlyHistoryItem[];
}

export interface DepartmentAnalytics {
  department_id: number;
  completion_rate: number;
  open_problems_count: number;
  total_planned_skills: number;
}

export function useUserAnalytics(userId: number | null) {
  return useQuery({
    queryKey: ['analytics', 'user', userId],
    queryFn: async () => {
      const { data } = await client.get<UserAnalytics>(`/analytics/user/${userId}`);
      return data;
    },
    enabled: userId !== null,
  });
}

export function useDepartmentAnalytics(departmentId: number | null) {
  return useQuery({
    queryKey: ['analytics', 'department', departmentId],
    queryFn: async () => {
      const { data } = await client.get<DepartmentAnalytics>(`/analytics/department/${departmentId}`);
      return data;
    },
    enabled: departmentId !== null,
  });
}