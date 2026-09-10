// src/api/types.ts

// ============================================================================
// 1. БАЗОВЫЕ ТИПЫ И ENUMS
// ============================================================================

/** Направления разработки (из требований кейса) */
export type Direction = 'BACK' | 'FRONT' | 'QA' | 'DEVOPS' | 'ANALYTICS';

/** Роль пользователя в системе */
export type UserRole = 'admin' | 'user';

/** Статусы скилла (точно как у бэкендера, с пробелом в 'IN TRAINING') */
export type SkillStatusEnum = 'PLANNED' | 'CONFIRMED' | 'IN TRAINING' | 'PROBLEM';

/** Статус встречи */
export type MeetingStatus = 'scheduled' | 'completed' | 'cancelled';

/** Тип вложения */
export type AttachmentType = 'file' | 'link';

// ============================================================================
// 2. ПОЛЬЗОВАТЕЛИ (USERS)
// ============================================================================

/** Профиль пользователя */
export interface User {
  id: number;
  full_name: string;
  email: string;
  direction: Direction;
  department_id: number;
  manager_id: number | null;
  role: UserRole;
}

/** Данные для создания пользователя */
export interface CreateUserDto {
  full_name: string;
  email: string;
  password: string;
  direction: Direction;
  department_id: number;
  manager_id?: number | null;
  role?: UserRole;
}

/** Публичный профиль сотрудника (для отображения) */
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

// ============================================================================
// 3. ПОДРАЗДЕЛЕНИЯ (DEPARTMENTS)
// ============================================================================

/** Подразделение (узел дерева) */
export interface Department {
  id: number;
  name: string;
  parent_id: number | null;
  head_id: number;
}

/** Данные для создания подразделения */
export interface CreateDepartmentDto {
  name: string;
  parent_id: number | null;
  head_id: number;
}

/** Подразделение с расширенной информацией */
export interface DepartmentWithDetails extends Department {
  head_name: string;
  employees_count: number;
  children?: DepartmentWithDetails[];
}

// ============================================================================
// 4. СКИЛЛЫ (SKILLS) - по схемам бэкендера
// ============================================================================

/** Скилл из справочника */
export interface SkillRead {
  id: number;
  name: string;
  department_id: number;
}

/** Данные для создания скилла */
export interface SkillCreate {
  name: string;
  department_id: number;
}

// ============================================================================
// 5. ГОДОВОЙ ПЛАН ОБУЧЕНИЯ - по схемам бэкендера
// ============================================================================

/** Элемент годового плана сотрудника */
export interface PlanItemRead {
  id: number;
  skill: SkillRead; // Вложенный объект
  target_date: string; // Формат 'YYYY-MM-DD'
  status: SkillStatusEnum;
  confirmed_at: string | null;
  problem_comment: string | null;
}

/** Данные для добавления навыка в план */
export interface PlanItemCreate {
  skill_id: number;
  target_date: string;
}

// ============================================================================
// 6. ВСТРЕЧИ 1:1 (MEETINGS / PR)
// ============================================================================

/** Вложение (файл или ссылка) */
export interface Attachment {
  type: AttachmentType;
  name: string;
  url: string;
}

/** Результат обсуждения скилла на встрече */
export interface MeetingSkillResult {
  skill_id: number;
  status: 'CONFIRMED' | 'PROBLEM' | 'DISCUSSED';
  comment?: string;
}

/** Протокол встречи 1:1 */
export interface Meeting {
  id: number;
  date: string;
  host_id: number;
  employee_id: number;
  markdown_notes: string;
  attachments: Attachment[];
  skills_reviewed: MeetingSkillResult[];
}

/** Данные для создания встречи */
export interface CreateMeetingDto {
  date: string;
  host_id: number;
  employee_id: number;
  markdown_notes?: string;
  attachments?: Attachment[];
  skills_reviewed?: MeetingSkillResult[];
}

// ============================================================================
// 7. АНАЛИТИКА (ANALYTICS)
// ============================================================================

/** Статистика по подразделению */
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

/** Прогресс по месяцам */
export interface MonthlyProgress {
  month: string;
  confirmed: number;
  planned: number;
}

/** Статистика по сотруднику */
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

/** Элемент временной шкалы скиллов */
export interface SkillTimelineItem {
  skill_id: number;
  skill_name: string;
  planned_date: string;
  confirmed_date?: string;
  status: SkillStatusEnum;
}

// ============================================================================
// 8. ФИЛЬТРЫ И ПАГИНАЦИЯ
// ============================================================================

/** Фильтры для списка сотрудников */
export interface EmployeeFilters {
  direction?: Direction;
  department_id?: number;
  search?: string;
}

/** Параметры пагинации */
export interface PaginationParams {
  page: number;
  limit: number;
}

/** Ответ с пагинацией */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// 9. КОНФИГУРАЦИЯ СТАТУСОВ (для UI)
// ============================================================================

/** Конфигурация статусов скилла для отображения */
export const SKILL_STATUS_CONFIG: Record<SkillStatusEnum, { color: string; text: string }> = {
  PLANNED: { color: 'blue', text: 'Запланирован' },
  CONFIRMED: { color: 'green', text: 'Зачтён' },
  'IN TRAINING': { color: 'orange', text: 'В процессе' },
  PROBLEM: { color: 'red', text: 'Проблема' },
};

/** Конфигурация направлений для отображения */
export const DIRECTION_CONFIG: Record<Direction, { color: string; text: string }> = {
  BACK: { color: 'green', text: 'Backend' },
  FRONT: { color: 'blue', text: 'Frontend' },
  QA: { color: 'purple', text: 'QA' },
  DEVOPS: { color: 'orange', text: 'DevOps' },
  ANALYTICS: { color: 'cyan', text: 'Analytics' },
};