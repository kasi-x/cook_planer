import { useState } from 'react';
import type { FoodItem } from '../types';

interface Props {
  foods: FoodItem[];
  selectedFoods: Set<string>;
  fixedFoods: Map<string, number>;
  onToggle: (name: string) => void;
  onSetFixed: (name: string, amount: number | null) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
}

export function FoodSelector({
  foods,
  selectedFoods,
  fixedFoods,
  onToggle,
  onSetFixed,
  onSelectAll,
  onClearAll,
}: Props) {
  const [editingFood, setEditingFood] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');

  const handleFixClick = (foodName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const currentAmount = fixedFoods.get(foodName);
    setInputValue(currentAmount ? currentAmount.toString() : '');
    setEditingFood(foodName);
  };

  const handleFixSubmit = (foodName: string, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const amount = parseFloat(inputValue);
    console.log('handleFixSubmit:', foodName, inputValue, amount);
    onSetFixed(foodName, isNaN(amount) ? null : amount);
    setEditingFood(null);
    setInputValue('');
  };

  const handleRemoveFixed = (foodName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onSetFixed(foodName, null);
  };

  const totalSelected = selectedFoods.size + fixedFoods.size;

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
          {totalSelected} / {foods.length} 選択中
          {fixedFoods.size > 0 && ` (固定: ${fixedFoods.size})`}
        </span>
      </div>

      <ul className="food-list">
        {foods.map((food) => {
          const isSelected = selectedFoods.has(food.food_name);
          const fixedAmount = fixedFoods.get(food.food_name);
          const isFixed = fixedAmount !== undefined;
          const isEditing = editingFood === food.food_name;

          return (
            <li key={food.food_name}>
              <label className={`${isSelected ? 'selected' : ''} ${isFixed ? 'fixed' : ''}`}>
                <input
                  type="checkbox"
                  checked={isSelected || isFixed}
                  onChange={() => {
                    if (isFixed) {
                      onSetFixed(food.food_name, null);
                    } else {
                      onToggle(food.food_name);
                    }
                  }}
                />
                <span className="food-info">
                  <span className="name">{food.food_name}</span>
                  <span className="price">
                    ¥{food.price_per_100g.toFixed(1)}/100g
                  </span>
                </span>
                {isEditing ? (
                  <div className="fixed-input" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleFixSubmit(food.food_name);
                        if (e.key === 'Escape') setEditingFood(null);
                      }}
                      placeholder="g"
                      autoFocus
                    />
                    <button type="button" onClick={(e) => handleFixSubmit(food.food_name, e)}>
                      確定
                    </button>
                  </div>
                ) : isFixed ? (
                  <span className="fixed-badge" onClick={(e) => handleFixClick(food.food_name, e)}>
                    固定: {fixedAmount}g
                    <button
                      type="button"
                      className="remove-fixed"
                      onClick={(e) => handleRemoveFixed(food.food_name, e)}
                    >
                      ×
                    </button>
                  </span>
                ) : (
                  <button
                    type="button"
                    className="fix-btn"
                    onClick={(e) => handleFixClick(food.food_name, e)}
                  >
                    固定
                  </button>
                )}
              </label>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
