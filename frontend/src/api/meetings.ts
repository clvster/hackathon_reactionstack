import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface Meeting {
  id: number;
  date: string;
  participant_ids: number[];
  participant_names: string[];
  summary_markdown: string;
  attachments: string[];
  skill_marks: { skill_id: number; skill_name: string; comment: string; status: 'confirmed' | 'problem' }[];
}

let MOCK_MEETINGS: Meeting[] = [
  {
    id: 1,
    date: '2026-01-15',
    participant_ids: [1, 2],
    participant_names: ['Иванов Иван Иванович', 'Петров Пётр Петрович'],
    summary_markdown: '## Итоги встречи\n\nОбсудили прогресс по **FastAPI**.',
    attachments: ['https://example.com/doc.pdf'],
    skill_marks: [{ skill_id: 1, skill_name: 'FastAPI', comment: 'Хорошо усвоено', status: 'confirmed' }],
  },
];

export function useMeetings() {
  return useQuery({
    queryKey: ['meetings'],
    queryFn: async () => MOCK_MEETINGS,
  });
}

export function useCreateMeeting() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Omit<Meeting, 'id' | 'participant_names'>) => {
      // TODO: заменить на реальный запрос POST /meetings
      const newMeeting: Meeting = {
        ...payload,
        id: Date.now(),
        participant_names: [],
      };
      MOCK_MEETINGS = [...MOCK_MEETINGS, newMeeting];
      return newMeeting;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
    },
  });
}