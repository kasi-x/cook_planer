import { useState, useEffect } from 'react';
import type { DailyMenuData, AllergenWarning as AllergenWarningType } from '../types';
import { checkAllergens } from '../api';

interface Props {
  menu: DailyMenuData;
  excludedAllergens: string[];
}

const SLOT_LABELS: Record<string, string> = {
  staple: '主食',
  main_dish: '主菜',
  side_dish: '副菜',
  soup: '汁物',
  dessert: 'デザート',
  milk: '牛乳',
};

export default function AllergenWarningPanel({ menu, excludedAllergens }: Props) {
  const [warnings, setWarnings] = useState<AllergenWarningType[]>([]);

  useEffect(() => {
    if (excludedAllergens.length === 0) {
      setWarnings([]);
      return;
    }
    checkAllergens(menu, excludedAllergens)
      .then(setWarnings)
      .catch(() => setWarnings([]));
  }, [menu, excludedAllergens]);

  if (excludedAllergens.length === 0 || warnings.length === 0) return null;

  return (
    <div className="allergen-warning-panel">
      <h4>アレルゲン警告</h4>
      {warnings.map((w, i) => (
        <div key={i} className={`allergen-warning-item ${w.severity}`}>
          <span className="allergen-warning-icon">
            {w.severity === 'mandatory' ? '!!' : '!'}
          </span>
          <span className="allergen-warning-text">
            <strong>{w.allergen}</strong> - {w.source_food}
            <span className="allergen-warning-slot">({SLOT_LABELS[w.slot] || w.slot})</span>
          </span>
        </div>
      ))}
    </div>
  );
}
