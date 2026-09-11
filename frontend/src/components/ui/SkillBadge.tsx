import { Tag } from 'antd';

type SkillStatusEnum = 'PLANNED' | 'COMPLETED' | 'IN TRAINING' | 'PROBLEM';

interface SkillBadgeProps {
  status: SkillStatusEnum;
}

const statusConfig: Record<SkillStatusEnum, { color: string; text: string }> = {
  PLANNED: { color: 'blue', text: 'Запланирован' },
  COMPLETED: { color: 'green', text: 'Зачтён' },
  'IN TRAINING': { color: 'orange', text: 'В процессе' },
  PROBLEM: { color: 'red', text: 'Проблема' },
};

export const SkillBadge: React.FC<SkillBadgeProps> = ({ status }) => {
  const config = statusConfig[status];
  return <Tag color={config.color}>{config.text}</Tag>;
};