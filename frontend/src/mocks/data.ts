export type Direction = 'BACK' | 'FRONT' | 'QA' | 'DEVOPS';
export type UserRole = 'admin' | 'user';

export interface Department {
  id: number;
  name: string;
  parent_id: number | null;
  head_id: number;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  direction: Direction;
  department_id: number;
  manager_id: number | null;
  role: UserRole;
}

export interface Meeting {
  id: number;
  date: string;
  host_id: number;
  employee_id: number;
  markdown_notes: string;
  attachments: { type: 'link' | 'file'; name: string; url: string }[];
  skills_reviewed: { skill_id: number; status: string; comment?: string }[];
}

import type{ 
  SkillRead, 
  PlanItemRead, 
} from '../api/types';


export const MOCK_DEPARTMENTS: Department[] = [
  { id: 1, name: 'ООО "ТехноСтарт"', parent_id: null, head_id: 1 },
  { id: 2, name: 'Департамент разработки', parent_id: 1, head_id: 2 },
  { id: 3, name: 'Отдел Frontend', parent_id: 2, head_id: 3 },
  { id: 4, name: 'Отдел Backend', parent_id: 2, head_id: 4 },
];

export const MOCK_USERS: User[] = [
  { 
    id: 1, 
    full_name: 'Смирнов Алексей', 
    email: 'ceo@tech.ru', 
    direction: 'BACK', 
    department_id: 1, 
    manager_id: null, 
    role: 'admin' 
  },
  { 
    id: 2, 
    full_name: 'Петрова Мария (CTO)', 
    email: 'cto@tech.ru', 
    direction: 'BACK', 
    department_id: 2, 
    manager_id: 1, 
    role: 'user' 
  },
  { 
    id: 3, 
    full_name: 'Иванов Дмитрий (Lead Front)', 
    email: 'lead@tech.ru', 
    direction: 'FRONT', 
    department_id: 3, 
    manager_id: 2, 
    role: 'user' 
  },
  { 
    id: 4, 
    full_name: 'Кузнецова Анна (Middle Front)', 
    email: 'anna@tech.ru', 
    direction: 'FRONT', 
    department_id: 3, 
    manager_id: 3, 
    role: 'user' 
  },
];

export const MOCK_SKILLS: SkillRead[] = [
  { id: 101, name: 'React Hooks', department_id: 3 },
  { id: 102, name: 'TypeScript Advanced', department_id: 3 },
  { id: 103, name: 'System Design', department_id: 2 },
  { id: 104, name: 'PostgreSQL Optimization', department_id: 4 },
];


export const MOCK_PLAN_ITEMS: PlanItemRead[] = [
  {
    id: 1,
    skill: { id: 101, name: 'React Hooks', department_id: 3 },
    target_date: '2024-03-01',
    status: "CONFIRMED",
    confirmed_at: '2024-02-28',
    problem_comment: null,
  },
  {
    id: 2,
    skill: { id: 102, name: 'TypeScript Advanced', department_id: 3 },
    target_date: '2024-06-15',
    status: 'IN TRAINING',
    confirmed_at: null,
    problem_comment: null,
  },
  {
    id: 3,
    skill: { id: 103, name: 'System Design', department_id: 2 },
    target_date: '2024-09-01',
    status: "PROBLEM",
    confirmed_at: null,
    problem_comment: 'Сложно дается проектирование микросервисов, нужна дополнительная литература',
  },
];


export const MOCK_MEETINGS = [
  {
    id: 1,
    date: '2024-02-28',
    host_id: 3, // Проводил Lead Front
    employee_id: 4, // С Анной
    markdown_notes: '## Итоги встречи\n\nАнна отлично закрыла задачу по хукам.\n- React Hooks: зачтено\n- TypeScript: есть вопросы по дженерикам',
    attachments: [{ url: 'https://example.com/docs', type: 'link', name: 'Ссылка на документацию' }],
    skills_reviewed: [
      { skill_id: 101, status: 'CONFIRMED', comment: 'Отличное знание' },
      { skill_id: 102, status: 'PROBLEM', comment: 'Нужно повторить дженерики' },
    ],
  }
];