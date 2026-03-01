interface Props {
  name: string;
  actual: number;
  standard: number;
  unit: string;
}

function getBarClass(ratio: number): string {
  if (ratio >= 100) return 'bar-green';
  if (ratio >= 80) return 'bar-yellow';
  return 'bar-red';
}

export default function NutrientBar({ name, actual, standard, unit }: Props) {
  const ratio = standard > 0 ? (actual / standard) * 100 : 0;
  const width = Math.min(ratio, 150);

  return (
    <div className="nutrient-row">
      <div className="nutrient-info">
        <span className="nutrient-name">{name}</span>
        <span className="nutrient-values">
          {actual.toFixed(1)}{unit} / {standard.toFixed(1)}{unit} ({ratio.toFixed(0)}%)
        </span>
      </div>
      <div className="nutrient-bar-track">
        <div
          className={`nutrient-bar-fill ${getBarClass(ratio)}`}
          style={{ width: `${Math.min(width, 100)}%` }}
        />
      </div>
    </div>
  );
}
