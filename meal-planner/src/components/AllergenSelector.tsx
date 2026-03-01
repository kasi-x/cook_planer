import { useState, useEffect } from 'react';
import type { AllergenInfo } from '../types';
import { fetchAllergens } from '../api';

interface Props {
  selected: string[];
  onChange: (allergens: string[]) => void;
}

export default function AllergenSelector({ selected, onChange }: Props) {
  const [allergens, setAllergens] = useState<AllergenInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAllergens()
      .then(setAllergens)
      .catch(() => setError('アレルゲン情報の読み込みに失敗しました'));
  }, []);

  const toggle = (id: string) => {
    if (selected.includes(id)) {
      onChange(selected.filter(a => a !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  const mandatory = allergens.filter(a => a.category === 'mandatory');
  const recommended = allergens.filter(a => a.category === 'recommended');

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="allergen-selector">
      <div className="allergen-group">
        <h4>特定原材料（8品目）</h4>
        <div className="allergen-chips">
          {mandatory.map(a => (
            <button
              key={a.id}
              className={`allergen-chip mandatory ${selected.includes(a.id) ? 'selected' : ''}`}
              onClick={() => toggle(a.id)}
            >
              {a.name}
            </button>
          ))}
        </div>
      </div>
      <div className="allergen-group">
        <h4>推奨表示（20品目）</h4>
        <div className="allergen-chips">
          {recommended.map(a => (
            <button
              key={a.id}
              className={`allergen-chip recommended ${selected.includes(a.id) ? 'selected' : ''}`}
              onClick={() => toggle(a.id)}
            >
              {a.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
