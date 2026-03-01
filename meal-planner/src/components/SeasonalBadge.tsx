import { useState, useEffect, useMemo } from 'react';
import type { DailyMenuData, SeasonalRecommendation } from '../types';
import { checkSeasonal } from '../api';

interface Props {
  menu: DailyMenuData;
  month: number;
  compact?: boolean;
}

export default function SeasonalBadge({ menu, month, compact = false }: Props) {
  const [recommendation, setRecommendation] = useState<SeasonalRecommendation | null>(null);

  // JSON.stringify をキーにして menu オブジェクト参照の変更による不要な再実行を防ぐ
  const menuKey = useMemo(() => JSON.stringify(menu), [menu]);

  useEffect(() => {
    checkSeasonal(menu, month)
      .then(setRecommendation)
      .catch(() => setRecommendation(null));
  }, [menuKey, month]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!recommendation) return null;

  if (compact) {
    const hasSeasonalItems = recommendation.seasonal_items.length > 0;
    if (!hasSeasonalItems) return null;
    return (
      <span className="seasonal-badge-compact" title="旬の食材を使用中">
        旬
      </span>
    );
  }

  return (
    <div className="seasonal-panel">
      <h4>旬の食材チェック</h4>
      <div className="seasonal-ratio">
        旬食材率: <strong>{recommendation.seasonal_ratio.toFixed(0)}%</strong>
      </div>

      {recommendation.seasonal_items.length > 0 && (
        <div className="seasonal-list seasonal-good">
          <span className="seasonal-label">旬:</span>
          {recommendation.seasonal_items.map((item, i) => (
            <span key={i} className="seasonal-tag in-season">{item.name}</span>
          ))}
        </div>
      )}

      {recommendation.non_seasonal_items.length > 0 && (
        <div className="seasonal-list seasonal-warn">
          <span className="seasonal-label">旬外:</span>
          {recommendation.non_seasonal_items.map((item, i) => (
            <span key={i} className="seasonal-tag off-season">{item.name}</span>
          ))}
        </div>
      )}

      {recommendation.suggestions.map((s, i) => (
        <div key={i} className="seasonal-suggestion">{s}</div>
      ))}
    </div>
  );
}
