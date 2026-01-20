import type { OptimizeResult } from '../types';
import { NutrientTable } from './NutrientTable';

interface Props {
  result: OptimizeResult | null;
  loading: boolean;
  error: string | null;
}

export function ResultPanel({ result, loading, error }: Props) {
  if (loading) {
    return (
      <section className="panel">
        <h2>最適化結果</h2>
        <div className="loading">計算中...</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel">
        <h2>最適化結果</h2>
        <div className="error">{error}</div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel">
        <h2>最適化結果</h2>
        <p className="placeholder">
          食材を選択して「最適化実行」ボタンを押してください
        </p>
      </section>
    );
  }

  if (!result.success) {
    return (
      <section className="panel">
        <h2>最適化結果</h2>
        <div className="error">{result.message}</div>
      </section>
    );
  }

  const sortedAmounts = Object.entries(result.amounts).sort(
    ([, a], [, b]) => b - a
  );

  return (
    <section className="panel">
      <h2>最適化結果</h2>

      <div className="amounts">
        <h3>推奨食材量（1日あたり）</h3>
        <ul>
          {sortedAmounts.map(([name, amount]) => (
            <li key={name}>
              <span className="name">{name}</span>
              <span className="value">{amount.toFixed(0)}g</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="cost-summary">
        <p>
          総コスト: <strong>¥{result.daily_cost}</strong>/日
          <span className="monthly">（約¥{result.monthly_cost}/月）</span>
        </p>
      </div>

      <NutrientTable nutrients={result.nutrients} />
    </section>
  );
}
