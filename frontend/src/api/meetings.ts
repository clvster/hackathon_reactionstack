import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { client } from './client';

export interface SkillAssessment {
  skill_id: number;
  is_completed: boolean;
  has_problem: boolean;
  comment?: string | null;
}

export interface Meeting {
  id: number;
  interviewer_id: number;
  participant_id: number;
  meeting_date: string;
  summary_markdown: string;
  files_and_links: string[];
}

export interface MeetingCreatePayload {
  participant_id: number;
  meeting_date: string;
  summary_markdown: string;
  files_and_links: string[];
  assessments: SkillAssessment[];
  global_problem_comment?: string | null;
}

export function useMeetings(filters?: { participant_id?: number; interviewer_id?: number }) {
  return useQuery({
    queryKey: ['meetings', filters],
    queryFn: async () => {
      const { data } = await client.get<Meeting[]>('/meetings', { params: filters });
      return data;
    },
  });
}

export function useCreateMeeting() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: MeetingCreatePayload) => {
      const { data } = await client.post<Meeting>('/meetings', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
    },
  });
}