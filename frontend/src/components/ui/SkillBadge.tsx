// src/components/ui/SkillBadge.tsx
import { Tag } from 'antd';
import type { SkillStatusEnum } from '../../api/types';

interface SkillBadgeProps {
  status: SkillStatusEnum;
}

const statusConfig: Record<SkillStatusEnum, { color: string; text: string }> = {
  PLANNED: { color: 'blue', text: 'Запланирован' },
  CONFIRMED: { color: 'green', text: 'Зачтён' },
  'IN TRAINING': { color: 'orange', text: 'В процессе' },
  PROBLEM: { color: 'red', text: 'Проблема' },
};

// ВАЖНО: именно export const, а не export default!
export const SkillBadge: React.FC<SkillBadgeProps> = ({ status }) => {
  const config = statusConfig[status];
  return <Tag color={config.color}>{config.text}</Tag>;
};