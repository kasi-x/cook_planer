import { useState, useEffect, useRef } from 'react';
import type { DailyMenuData, CookingEffortResult } from '../types';
import { estimateCookingEffort } from '../api';

interface Props {
  menu: DailyMenuData;
}

export default function CookingEffort({ menu }: Props) {
  const [effort, setEffort] = useState<CookingEffortResult | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      estimateCookingEffort(menu)
        .then(setEffort)
        .catch(() => setEffort(null));
    }, 800);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [menu]);

  if (!effort || effort.slots_detail.length === 0) return null;

  return (
    <div className="cooking-effort-panel">
      <h4>調理工数</h4>
      <div className="effort-summary">
        <div className="effort-stat">
          <span className="effort-label">調理時間</span>
          <span className="effort-value">{effort.parallel_minutes}分</span>
          <span className="effort-sub">(並行調理時)</span>
        </div>
        <div className="effort-stat">
          <span className="effort-label">難易度</span>
          <span className={`effort-value effort-${effort.difficulty <= 2 ? 'easy' : effort.difficulty <= 3.5 ? 'normal' : 'hard'}`}>
            {effort.difficulty_label}
          </span>
        </div>
      </div>

      <div className="effort-detail">
        <div className="effort-breakdown">
          下処理: {effort.prep_minutes}分 / 調理: {effort.cook_minutes}分
        </div>
        {effort.slots_detail.map((slot, i) => (
          <div key={i} className="effort-slot">
            <span className="effort-slot-name">{slot.slot_label}</span>
            <span className="effort-slot-method">{slot.method}</span>
            <span className="effort-slot-time">{slot.total_minutes}分</span>
          </div>
        ))}
      </div>

      {effort.suggestions.length > 0 && (
        <div className="effort-suggestions">
          {effort.suggestions.map((s, i) => (
            <div key={i} className="effort-suggestion">
              {s.suggestion}
              {s.time_saved > 0 && <span className="effort-saved">（-{s.time_saved}分）</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
