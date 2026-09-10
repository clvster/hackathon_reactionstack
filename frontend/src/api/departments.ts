import { useQuery } from '@tanstack/react-query';

export interface Department {
  id: number;
  name: string;
  parent_id: number | null;
  leader_id: number | null;
  
}

// Временные моковые данные
const MOCK_DEPARTMENTS: Department[] = [
    
    { id: 1, name: 'Разработка', parent_id: null, leader_id: 1 },
    { id: 2, name: 'Backend', parent_id: 1, leader_id: 2 },
    { id: 3, name: 'Frontend', parent_id: 1, leader_id: 3 },
    { id: 4, name: 'QA', parent_id: 1, leader_id: 4 },

];

export function useDepartments() {
  return useQuery({
    queryKey: ['departments'],
    queryFn: async () => {
    
        // заменить на реальный запрос РЕАЛЬНО НЕ ЗАБЫЫЫЫЫТЬ
        // const { data } = await client.get<Department[]>('/departments');
        // return data;

        return MOCK_DEPARTMENTS;
    },
  });
}