import type { SchoolGradeLevel } from '../types';
import { GRADE_LABELS } from '../types';

interface Props {
  value: SchoolGradeLevel;
  onChange: (grade: SchoolGradeLevel) => void;
}

export default function GradeSelector({ value, onChange }: Props) {
  return (
    <div className="grade-selector">
      <select value={value} onChange={e => onChange(e.target.value as SchoolGradeLevel)}>
        {(Object.entries(GRADE_LABELS) as [SchoolGradeLevel, string][]).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>
    </div>
  );
}
