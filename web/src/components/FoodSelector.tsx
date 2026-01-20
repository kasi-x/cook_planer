import type { FoodItem } from '../types';

interface Props {
  foods: FoodItem[];
  selectedFoods: Set<string>;
  onToggle: (name: string) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
}

export function FoodSelector({
  foods,
  selectedFoods,
  onToggle,
  onSelectAll,
  onClearAll,
}: Props) {
  return (
    <section className="panel">
      <h2>食材選択</h2>

      <div className="select-actions">
        <button type="button" onClick={onSelectAll}>
          すべて選択
        </button>
        <button type="button" onClick={onClearAll}>
          すべて解除
        </button>
        <span className="count">
          {selectedFoods.size} / {foods.length} 選択中
        </span>
      </div>

      <ul className="food-list">
        {foods.map((food) => {
          const isSelected = selectedFoods.has(food.food_name);
          return (
            <li key={food.food_name}>
              <label className={isSelected ? 'selected' : ''}>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggle(food.food_name)}
                />
                <span className="food-info">
                  <span className="name">{food.food_name}</span>
                  <span className="price">
                    ¥{food.price_per_100g.toFixed(1)}/100g
                  </span>
                </span>
              </label>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
