import type { NutrientStatus } from '../types';

interface Props {
  nutrients: NutrientStatus[];
}

export function NutrientTable({ nutrients }: Props) {
  return (
    <div className="nutrient-section">
      <h3>栄養素達成状況</h3>
      <table className="nutrient-table">
        <thead>
          <tr>
            <th>栄養素</th>
            <th>摂取量</th>
            <th>目標</th>
            <th>達成率</th>
            <th>状態</th>
          </tr>
        </thead>
        <tbody>
          {nutrients.map((n) => (
            <tr key={n.name}>
              <td>{n.name}</td>
              <td>
                {n.actual} {n.unit}
              </td>
              <td>
                {n.required} {n.unit}
              </td>
              <td>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${n.achieved ? 'complete' : ''}`}
                    style={{ width: `${Math.min(n.ratio, 100)}%` }}
                  />
                </div>
                <span>{n.ratio.toFixed(0)}%</span>
              </td>
              <td className={n.achieved ? 'status-ok' : 'status-ng'}>
                {n.achieved ? 'OK' : 'NG'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
