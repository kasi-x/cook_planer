import { useState } from 'react';
import type { NutrientStatus, FoodContribution } from '../types';

interface Props {
  nutrients: NutrientStatus[];
}

const COLORS = [
  '#3498db', // blue
  '#e74c3c', // red
  '#2ecc71', // green
  '#f39c12', // orange
  '#9b59b6', // purple
  '#1abc9c', // teal
  '#e67e22', // dark orange
  '#34495e', // dark gray
];

function getColor(index: number): string {
  return COLORS[index % COLORS.length];
}

function ContributionBar({
  contributions,
  ratio,
  unit,
}: {
  contributions: FoodContribution[];
  ratio: number;
  unit: string;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // バーの最大値は100%または実際の達成率のうち大きい方
  const maxRatio = Math.max(100, ratio);
  // 100%ラインの位置（%）
  const hundredPercentPosition = (100 / maxRatio) * 100;

  return (
    <div className="contribution-container">
      <div className="contribution-bar-wrapper">
        <div className="contribution-bar">
          {contributions.map((c, i) => {
            // 各セグメントの幅をmaxRatioに対する割合で計算
            const segmentWidth = (c.percentage / maxRatio) * 100;
            return (
              <div
                key={c.food_name}
                className={`contribution-segment ${hoveredIndex === i ? 'hovered' : ''}`}
                style={{
                  width: `${segmentWidth}%`,
                  backgroundColor: getColor(i),
                }}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                {hoveredIndex === i && (
                  <div className="contribution-tooltip">
                    <strong>{c.food_name}</strong> ({c.amount}g)
                    <br />
                    {c.contribution} {unit} ({c.percentage}%)
                  </div>
                )}
              </div>
            );
          })}
          {ratio < 100 && (
            <div
              className="contribution-segment empty"
              style={{ width: `${((100 - ratio) / maxRatio) * 100}%` }}
            />
          )}
        </div>
        {/* 100%ラインのマーカー */}
        {ratio > 100 && (
          <div
            className="hundred-percent-marker"
            style={{ left: `${hundredPercentPosition}%` }}
          >
            <span className="marker-label">100%</span>
          </div>
        )}
      </div>
      <div className="contribution-legend">
        {contributions.map((c, i) => (
          <span
            key={c.food_name}
            className={`legend-item ${hoveredIndex === i ? 'hovered' : ''}`}
            onMouseEnter={() => setHoveredIndex(i)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <span
              className="legend-color"
              style={{ backgroundColor: getColor(i) }}
            />
            <span className="legend-text">
              {c.food_name}: {c.percentage}%
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

export function NutrientTable({ nutrients }: Props) {
  return (
    <div className="nutrient-section">
      <h3>栄養素達成状況</h3>
      <div className="nutrient-cards">
        {nutrients.map((n) => (
          <div
            key={n.name}
            className={`nutrient-card ${n.achieved ? 'achieved' : 'not-achieved'}`}
          >
            <div className="nutrient-header">
              <span className="nutrient-name">{n.name}</span>
              <span className={`nutrient-status ${n.achieved ? 'ok' : 'ng'}`}>
                {n.achieved ? 'OK' : 'NG'}
              </span>
            </div>
            <div className="nutrient-values">
              <span className="actual">
                {n.actual} {n.unit}
              </span>
              <span className="separator">/</span>
              <span className="required">
                {n.required} {n.unit}
              </span>
              <span className="ratio">({n.ratio.toFixed(0)}%)</span>
            </div>
            <ContributionBar contributions={n.contributions} ratio={n.ratio} unit={n.unit} />
          </div>
        ))}
      </div>
    </div>
  );
}
