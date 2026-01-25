import { useState } from 'react';
import type { OptimizeResult } from '../types';
import { NutrientTable } from './NutrientTable';

interface Props {
  result: OptimizeResult | null;
  loading: boolean;
  error: string | null;
}

export function ResultPanel({ result, loading, error }: Props) {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyToClipboard = () => {
    if (!result || !result.success) return;

    const lines = [
      '【栄養最適化結果】',
      '',
      '■ 推奨食材量:',
      ...result.food_amounts.map(
        (f) => `  ${f.food_name}: ${f.amount_g.toFixed(0)}g (¥${f.cost})`
      ),
      '',
      `■ 総コスト: ¥${result.daily_cost}/日 (約¥${result.monthly_cost}/月)`,
      '',
      '■ 栄養素達成状況:',
      ...result.nutrients.map(
        (n) =>
          `  ${n.name}: ${n.actual}${n.unit} / ${n.required}${n.unit} (${n.ratio}%) ${n.achieved ? '✓' : ''}`
      ),
    ];

    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    });
  };

  const handleExportCSV = () => {
    if (!result || !result.success) return;

    // Food amounts CSV
    const foodHeader = '食材名,量(g),価格(円),貢献度(%)';
    const foodRows = result.food_amounts.map(
      (f) => `${f.food_name},${f.amount_g.toFixed(0)},${f.cost},${f.contribution_percent.toFixed(1)}`
    );

    // Nutrients CSV
    const nutrientHeader = '\n\n栄養素,摂取量,目標値,単位,達成率(%),達成';
    const nutrientRows = result.nutrients.map(
      (n) => `${n.name},${n.actual},${n.required},${n.unit},${n.ratio},${n.achieved ? '○' : '×'}`
    );

    const csv = [
      foodHeader,
      ...foodRows,
      nutrientHeader,
      ...nutrientRows,
      '',
      `総コスト(日),${result.daily_cost}`,
      `総コスト(月),${result.monthly_cost}`,
    ].join('\n');

    // BOM for Excel compatibility
    const bom = '\uFEFF';
    const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `栄養最適化_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <section className="panel">
        <h2>最適化結果</h2>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>計算中...</p>
        </div>
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

  const achievedCount = result.nutrients.filter((n) => n.achieved).length;
  const totalNutrients = result.nutrients.length;

  return (
    <section className="panel result-panel">
      <div className="result-header">
        <h2>最適化結果</h2>
        <div className="export-buttons">
          <button
            type="button"
            className="btn-export"
            onClick={handleCopyToClipboard}
            title="クリップボードにコピー"
          >
            {copySuccess ? 'コピー完了!' : 'コピー'}
          </button>
          <button
            type="button"
            className="btn-export"
            onClick={handleExportCSV}
            title="CSVファイルでダウンロード"
          >
            CSV出力
          </button>
        </div>
      </div>

      <div className="result-summary">
        <span className={`achievement-badge ${achievedCount === totalNutrients ? 'complete' : ''}`}>
          {achievedCount}/{totalNutrients} 栄養素達成
        </span>
        <span className="message">{result.message}</span>
      </div>

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
                  <span className="source-price" title={food.source_price ? `価格: ${food.source_price}` : '価格データなし'}>
                    {food.source_price ? food.source_price.slice(0, 12) : '-'}
                  </span>
                  <span className="source-nutrition" title={food.source_nutrition ? `栄養: ${food.source_nutrition}` : '栄養データなし'}>
                    {food.source_nutrition ? food.source_nutrition.slice(0, 12) : '-'}
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
