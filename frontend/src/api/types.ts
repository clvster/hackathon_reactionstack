export type Direction = 'BACK' | 'FRONT' | 'QA' | 'DEVOPS' | 'ANALYTICS';

export type UserRole = 'admin' | 'user';

export type SkillStatusEnum = 'PLANNED' | 'CONFIRMED' | 'IN TRAINING' | 'PROBLEM';

export type MeetingStatus = 'scheduled' | 'completed' | 'cancelled';

export type AttachmentType = 'file' | 'link';

export interface User {
  id: number;
  full_name: string;
  email: string;
  direction: Direction;
  department_id: number;
  manager_id: number | null;
  role: UserRole;
}

export interface CreateUserDto {
  full_name: string;
  email: string;
  password: string;
  direction: Direction;
  department_id: number;
  manager_id?: number | null;
  role?: UserRole;
}

export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  direction: Direction;
  department_id: number;
  department_name?: string;
  manager_id: number | null;
  manager_name?: string;
}

export interface Department {
  id: number;
  name: string;
  parent_id: number | null;
  head_id: number;
}

export interface CreateDepartmentDto {
  name: string;
  parent_id: number | null;
  head_id: number;
}

export interface DepartmentWithDetails extends Department {
  head_name: string;
  employees_count: number;
  children?: DepartmentWithDetails[];
}

export interface SkillRead {
  id: number;
  name: string;
  department_id: number;
}

export interface SkillCreate {
  name: string;
  department_id: number;
}

export interface PlanItemRead {
  id: number;
  skill: SkillRead; // Вложенный объект
  target_date: string; // Формат 'YYYY-MM-DD'
  status: SkillStatusEnum;
  confirmed_at: string | null;
  problem_comment: string | null;
}

export interface PlanItemCreate {
  skill_id: number;
  target_date: string;
}

export interface Attachment {
  type: AttachmentType;
  name: string;
  url: string;
}

export interface MeetingSkillResult {
  skill_id: number;
  status: 'CONFIRMED' | 'PROBLEM' | 'DISCUSSED';
  comment?: string;
}

export interface Meeting {
  id: number;
  date: string;
  host_id: number;
  employee_id: number;
  markdown_notes: string;
  attachments: Attachment[];
  skills_reviewed: MeetingSkillResult[];
}

export interface CreateMeetingDto {
  date: string;
  host_id: number;
  employee_id: number;
  markdown_notes?: string;
  attachments?: Attachment[];
  skills_reviewed?: MeetingSkillResult[];
}

export interface DepartmentAnalytics {
  department_id: number;
  department_name: string;
  total_employees: number;
  total_skills: number;
  confirmed_skills: number;
  problem_skills: number;
  completion_rate: number;
  monthly_progress: MonthlyProgress[];
}

export interface MonthlyProgress {
  month: string;
  confirmed: number;
  planned: number;
}

export interface EmployeeAnalytics {
  employee_id: number;
  employee_name: string;
  direction: Direction;
  total_skills: number;
  confirmed_skills: number;
  in_progress_skills: number;
  problem_skills: number;
  completion_rate: number;
  skills_timeline: SkillTimelineItem[];
}

export interface SkillTimelineItem {
  skill_id: number;
  skill_name: string;
  planned_date: string;
  confirmed_date?: string;
  status: SkillStatusEnum;
}
export interface EmployeeFilters {
  direction?: Direction;
  department_id?: number;
  search?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export const SKILL_STATUS_CONFIG: Record<SkillStatusEnum, { color: string; text: string }> = {
  PLANNED: { color: 'blue', text: 'Запланирован' },
  CONFIRMED: { color: 'green', text: 'Зачтён' },
  'IN TRAINING': { color: 'orange', text: 'В процессе' },
  PROBLEM: { color: 'red', text: 'Проблема' },
};

export const DIRECTION_CONFIG: Record<Direction, { color: string; text: string }> = {
  BACK: { color: 'green', text: 'Backend' },
  FRONT: { color: 'blue', text: 'Frontend' },
  QA: { color: 'purple', text: 'QA' },
  DEVOPS: { color: 'orange', text: 'DevOps' },
  ANALYTICS: { color: 'cyan', text: 'Analytics' },
};