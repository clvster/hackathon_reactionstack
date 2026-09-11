import { Progress } from 'antd';

interface SkillProgressBarProps {
  percent: number; // 0-100
  label?: string;
}

export default function SkillProgressBar({ percent, label }: SkillProgressBarProps) {
  const strokeColor = percent >= 80 ? '#52c41a' : percent >= 40 ? '#faad14' : '#ff4d4f';

  return (
    <div style={{ marginBottom: 8 }}>
      {label && <div style={{ marginBottom: 4, fontSize: 13 }}>{label}</div>}
      <Progress percent={percent} strokeColor={strokeColor} />
    </div>
  );
}