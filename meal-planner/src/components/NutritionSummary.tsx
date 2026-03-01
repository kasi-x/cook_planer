import type { DailyNutritionResult } from '../types';
import NutrientBar from './NutrientBar';

interface Props {
  nutrition: DailyNutritionResult | null;
  loading: boolean;
}

export default function NutritionSummary({ nutrition, loading }: Props) {
  if (loading) {
    return (
      <div className="nutrition-panel">
        <h3>栄養分析</h3>
        <p style={{ color: '#636e72', fontSize: 13 }}>計算中...</p>
      </div>
    );
  }

  if (!nutrition) {
    return (
      <div className="nutrition-panel">
        <h3>栄養分析</h3>
        <p style={{ color: '#636e72', fontSize: 13 }}>食材を追加すると栄養値が表示されます</p>
      </div>
    );
  }

  return (
    <div className="nutrition-panel">
      <h3>栄養分析</h3>
      <div className="nutrient-list">
        {nutrition.nutrients.map(n => (
          <NutrientBar
            key={n.key}
            name={n.name}
            actual={n.actual}
            standard={n.standard}
            unit={n.unit}
          />
        ))}
      </div>
      <div className="nutrition-cost">
        食材費: &yen;{nutrition.total_cost.toFixed(0)}
      </div>
      <div className="achievement-summary">
        基準達成率: {nutrition.achievement_rate.toFixed(0)}%
      </div>
    </div>
  );
}
