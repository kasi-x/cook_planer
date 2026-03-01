import { useState, useEffect, useRef } from 'react';
import type { DailyMenuData, CombinationResult } from '../types';
import { checkCombinations } from '../api';

interface Props {
  menu: DailyMenuData;
}

export default function CombinationCheck({ menu }: Props) {
  const [result, setResult] = useState<CombinationResult | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      checkCombinations(menu)
        .then(setResult)
        .catch(() => setResult(null));
    }, 800);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [menu]);

  if (!result) return null;
  if (result.good_effects.length === 0 && result.bad_effects.length === 0) return null;

  return (
    <div className="combination-panel">
      <h4>食べ合わせ</h4>

      {result.good_effects.map((effect, i) => (
        <div key={`good-${i}`} className="combination-item combination-good">
          <span className="combination-icon">+</span>
          <span className="combination-text">{effect.description}</span>
        </div>
      ))}

      {result.bad_effects.map((effect, i) => (
        <div key={`bad-${i}`} className="combination-item combination-bad">
          <span className="combination-icon">-</span>
          <span className="combination-text">{effect.description}</span>
        </div>
      ))}

      {result.suggestions.length > 0 && (
        <div className="combination-suggestions">
          {result.suggestions.map((s, i) => (
            <div key={i} className="combination-suggestion">{s}</div>
          ))}
        </div>
      )}
    </div>
  );
}
