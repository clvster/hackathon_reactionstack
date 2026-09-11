import { useQuery } from '@tanstack/react-query';

export interface AnalyticsPoint {
  month: string;
  progress: number;
}

const MOCK_TEAM_PROGRESS: AnalyticsPoint[] = [
  { month: 'Янв', progress: 20 },
  { month: 'Фев', progress: 35 },
  { month: 'Мар', progress: 50 },
  { month: 'Апр', progress: 68 },
  { month: 'Май', progress: 75 },
];

export function useTeamProgress(departmentId: number | null) {
  return useQuery({
    queryKey: ['analytics', 'team', departmentId],
    queryFn: async () => MOCK_TEAM_PROGRESS,
    enabled: departmentId !== null,
  });
}

export function useUserProgress(userId: number | null) {
  return useQuery({
    queryKey: ['analytics', 'user', userId],
    queryFn: async () => MOCK_TEAM_PROGRESS.map((p) => ({ ...p, progress: p.progress - 10 })),
    enabled: userId !== null,
  });
}