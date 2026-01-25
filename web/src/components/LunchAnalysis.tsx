import { useMemo } from 'react';

interface NutrientComparison {
  name: string;
  key: string;
  lunchStandard: number;
  dailyRequirement: number;
  unit: string;
  ratio: number; // 給食/1日 (%)
  expectedRatio: number; // 期待値（1食=33.3%）
  gap: number; // 不足/過剰 (%)
}

interface Props {
  age: number;
  gender: 'male' | 'female';
  lunchData: Record<string, number>;
  dailyData: Record<string, number>;
}

const NUTRIENT_INFO: Record<string, { name: string; unit: string; importance: string }> = {
  energy_kcal: { name: 'エネルギー', unit: 'kcal', importance: '成長・活動の源' },
  protein_g: { name: 'たんぱく質', unit: 'g', importance: '筋肉・臓器の材料' },
  calcium_mg: { name: 'カルシウム', unit: 'mg', importance: '骨・歯の形成' },
  iron_mg: { name: '鉄', unit: 'mg', importance: '貧血予防・酸素運搬' },
  vitamin_a_ug: { name: 'ビタミンA', unit: 'μg', importance: '視力・免疫機能' },
  vitamin_c_mg: { name: 'ビタミンC', unit: 'mg', importance: '免疫・コラーゲン生成' },
  vitamin_b1_mg: { name: 'ビタミンB1', unit: 'mg', importance: '糖質代謝・疲労回復' },
  vitamin_b2_mg: { name: 'ビタミンB2', unit: 'mg', importance: '成長促進・皮膚健康' },
  fiber_g: { name: '食物繊維', unit: 'g', importance: '腸内環境・便秘予防' },
  zinc_mg: { name: '亜鉛', unit: 'mg', importance: '成長・味覚・免疫' },
};

// 重点栄養素（問題提起に使用）
const FOCUS_NUTRIENTS = [
  'energy_kcal',
  'protein_g',
  'calcium_mg',
  'iron_mg',
  'vitamin_a_ug',
  'vitamin_c_mg',
];

export function LunchAnalysis({ age, gender, lunchData, dailyData }: Props) {
  const comparisons = useMemo(() => {
    const result: NutrientComparison[] = [];
    const expectedRatio = 33.3; // 1日3食なら各食33.3%が期待値

    for (const key of FOCUS_NUTRIENTS) {
      const info = NUTRIENT_INFO[key];
      if (!info) continue;

      const lunchStandard = lunchData[key] || 0;
      const dailyRequirement = dailyData[key] || 0;

      if (dailyRequirement === 0) continue;

      const ratio = (lunchStandard / dailyRequirement) * 100;
      const gap = ratio - expectedRatio;

      result.push({
        name: info.name,
        key,
        lunchStandard,
        dailyRequirement,
        unit: info.unit,
        ratio,
        expectedRatio,
        gap,
      });
    }

    return result;
  }, [lunchData, dailyData]);

  // 問題の深刻度を計算
  const severeDeficits = comparisons.filter((c) => c.gap < -10);
  const moderateDeficits = comparisons.filter((c) => c.gap >= -10 && c.gap < 0);
  const adequate = comparisons.filter((c) => c.gap >= 0);

  const avgGap = comparisons.reduce((sum, c) => sum + c.gap, 0) / comparisons.length;

  return (
    <section className="panel lunch-analysis">
      <h2>給食栄養分析</h2>

      <div className="analysis-header">
        <div className="target-info">
          <span className="age-badge">{age}歳</span>
          <span className="gender-badge">{gender === 'male' ? '男子' : '女子'}</span>
        </div>
        <p className="analysis-subtitle">
          学校給食基準 vs 1日の必要摂取量
        </p>
      </div>

      {/* 問題提起サマリー */}
      <div className="problem-summary">
        <div className="summary-stat severe">
          <span className="stat-number">{severeDeficits.length}</span>
          <span className="stat-label">深刻な不足</span>
        </div>
        <div className="summary-stat warning">
          <span className="stat-number">{moderateDeficits.length}</span>
          <span className="stat-label">やや不足</span>
        </div>
        <div className="summary-stat ok">
          <span className="stat-number">{adequate.length}</span>
          <span className="stat-label">基準達成</span>
        </div>
      </div>

      {avgGap < 0 && (
        <div className="problem-statement">
          <p>
            <strong>問題:</strong> 給食は1日の1/3（33.3%）を担うべきですが、
            平均<strong>{Math.abs(avgGap).toFixed(1)}%不足</strong>しています。
            特に<strong>{severeDeficits.map(d => d.name).join('・')}</strong>が深刻です。
          </p>
        </div>
      )}

      {/* 栄養素別比較 */}
      <div className="nutrient-comparison-list">
        <div className="comparison-header">
          <span>栄養素</span>
          <span>給食基準</span>
          <span>1日必要量</span>
          <span>充足率</span>
          <span>評価</span>
        </div>

        {comparisons.map((comp) => {
          const isDeficit = comp.gap < 0;
          const isSevere = comp.gap < -10;
          const statusClass = isSevere ? 'severe' : isDeficit ? 'warning' : 'ok';

          return (
            <div key={comp.key} className={`comparison-row ${statusClass}`}>
              <span className="nutrient-name">
                {comp.name}
                <small className="nutrient-importance">
                  {NUTRIENT_INFO[comp.key]?.importance}
                </small>
              </span>
              <span className="nutrient-value">
                {comp.lunchStandard.toFixed(1)}{comp.unit}
              </span>
              <span className="nutrient-value">
                {comp.dailyRequirement.toFixed(1)}{comp.unit}
              </span>
              <span className="nutrient-ratio">
                <div className="ratio-bar-container">
                  <div
                    className={`ratio-bar ${statusClass}`}
                    style={{ width: `${Math.min(comp.ratio, 100)}%` }}
                  />
                  <div className="expected-marker" style={{ left: '33.3%' }} />
                </div>
                <span className="ratio-text">{comp.ratio.toFixed(1)}%</span>
              </span>
              <span className={`nutrient-status ${statusClass}`}>
                {isSevere ? '不足' : isDeficit ? 'やや不足' : '適正'}
                <small>{comp.gap >= 0 ? '+' : ''}{comp.gap.toFixed(1)}%</small>
              </span>
            </div>
          );
        })}
      </div>

      {/* 解説 */}
      <div className="analysis-explanation">
        <h4>この分析の意味</h4>
        <ul>
          <li>
            <strong>期待値33.3%</strong>: 1日3食として、給食は1日の栄養の1/3を担うべき
          </li>
          <li>
            <strong>実際の給食基準</strong>: 多くの栄養素で30%前後に留まっている
          </li>
          <li>
            <strong>問題</strong>: 朝食欠食の子どもは、給食だけで栄養を補えない
          </li>
        </ul>
      </div>
    </section>
  );
}
