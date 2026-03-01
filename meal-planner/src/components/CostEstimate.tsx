import { useState, useEffect, useRef } from 'react';
import type { DailyMenuData, MenuCostEstimate } from '../types';
import { estimateMenuCost } from '../api';

interface Props {
  menu: DailyMenuData;
  month: number;
  bufferPct?: number;
}

const SLOT_LABELS: Record<string, string> = {
  staple: '主食',
  main_dish: '主菜',
  side_dish: '副菜',
  soup: '汁物',
  dessert: 'デザート',
  milk: '牛乳',
};

export default function CostEstimate({ menu, month, bufferPct = 10 }: Props) {
  const [estimate, setEstimate] = useState<MenuCostEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      estimateMenuCost(menu, month, bufferPct)
        .then(setEstimate)
        .catch(() => setEstimate(null))
        .finally(() => setLoading(false));
    }, 800);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [menu, month, bufferPct]);

  if (loading) {
    return <div className="cost-estimate-panel"><h4>コスト推定</h4><p className="cost-loading">計算中...</p></div>;
  }

  if (!estimate || estimate.items.length === 0) return null;

  return (
    <div className="cost-estimate-panel">
      <h4>コスト推定（{month}月）</h4>
      <div className="cost-summary">
        <div className="cost-row">
          <span>予測コスト</span>
          <span className="cost-value">&yen;{Math.round(estimate.total_cost)}</span>
        </div>
        <div className="cost-row cost-buffered">
          <span>バッファー込み（+{estimate.buffer_pct.toFixed(0)}%）</span>
          <span className="cost-value">&yen;{Math.round(estimate.buffered_total_cost)}</span>
        </div>
      </div>
      <div className="cost-items">
        {estimate.items.map((item, i) => (
          <div key={i} className="cost-item">
            <span className="cost-item-slot">{SLOT_LABELS[item.slot] || item.slot}</span>
            <span className="cost-item-food">{item.food_name}</span>
            <span className="cost-item-amount">{item.amount_g}g</span>
            <span className="cost-item-price">&yen;{Math.round(item.cost)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
