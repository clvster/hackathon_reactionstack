import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { client } from './client';

export interface Skill {
  id: number;
  name: string;
  direction_id: number;
}

export type SkillStatus = 'PLANNED' | 'COMPLETED' | 'IN TRAINING' | 'PROBLEM';

export interface PlanItem {
  id: number;
  skill: Skill;
  target_date: string;
  status: SkillStatus;
  confirmed_at: string | null;
  problem_comment: string | null;
}

export function useSkills(directionId?: number) {
  return useQuery({
    queryKey: ['skills', directionId],
    queryFn: async () => {
      const { data } = await client.get<Skill[]>('/skills', {
        params: directionId ? { direction_id: directionId } : undefined,
      });
      return data;
    },
  });
}

export function useCreateSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { name: string; direction_id: number }) => {
      const { data } = await client.post<Skill>('/skills', payload);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['skills'] }),
  });
}

export function useUpdateSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: number; name?: string; direction_id?: number }) => {
      const { data } = await client.patch<Skill>(`/skills/${id}`, payload);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['skills'] }),
  });
}

export function useUserPlan(userId: number | undefined) {
  return useQuery({
    queryKey: ['plan', userId],
    queryFn: async () => {
      const { data } = await client.get<PlanItem[]>(`/users/${userId}/plan`);
      return data;
    },
    enabled: userId !== undefined,
  });
}

export function useAddSkillsToPlan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      userId,
      items,
    }: {
      userId: number;
      items: { skill_id: number; target_date: string }[];
    }) => {
      const { data } = await client.post<PlanItem[]>(`/users/${userId}/plan`, items);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['plan', variables.userId] });
    },
  });
}