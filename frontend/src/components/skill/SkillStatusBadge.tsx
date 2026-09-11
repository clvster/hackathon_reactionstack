import { Tag } from 'antd';

type SkillStatus = 'planned' | 'confirmed' | 'problem';

const STATUS_CONFIG: Record<SkillStatus, { color: string; label: string }> = {
  planned: { color: 'blue', label: 'Запланирован' },
  confirmed: { color: 'green', label: 'Зачтён' },
  problem: { color: 'red', label: 'Проблема' },
};

interface SkillStatusBadgeProps {
  status: SkillStatus;
}

export default function SkillStatusBadge({ status }: SkillStatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  return <Tag color={config.color}>{config.label}</Tag>;
}