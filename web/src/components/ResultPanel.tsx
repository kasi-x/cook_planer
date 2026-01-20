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

  return (
    <section className="panel">
      <h2>最適化結果</h2>

      <div className="amounts">
        <h3>推奨食材量（1日あたり）</h3>
        <table className="food-amounts-table">
          <thead>
            <tr>
              <th>食材</th>
              <th>量</th>
              <th>価格</th>
              <th>貢献度</th>
              <th>データソース</th>
            </tr>
          </thead>
          <tbody>
            {result.food_amounts.map((food) => (
              <tr key={food.food_name}>
                <td className="food-name">{food.food_name}</td>
                <td className="amount">{food.amount_g.toFixed(0)}g</td>
                <td className="cost">¥{food.cost}</td>
                <td className="contribution">
                  <div className="contrib-bar-wrapper">
                    <div
                      className="contrib-bar"
                      style={{ width: `${Math.min(food.contribution_percent, 100)}%` }}
                    />
                    <span>{food.contribution_percent.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="sources">
                  <span className="source-price" title={`価格: ${food.source_price}`}>
                    {food.source_price.slice(0, 12)}
                  </span>
                  <span className="source-nutrition" title={`栄養: ${food.source_nutrition}`}>
                    {food.source_nutrition.slice(0, 12)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
