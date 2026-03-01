import { useState } from 'react';
import type { MealItem, MealIngredient, FoodItem, Recipe, MealSlotType } from '../types';
import { MEAL_SLOT_LABELS, emptyMealItem } from '../types';
import DishSelector from './DishSelector';

interface Props {
  slotType: MealSlotType;
  item: MealItem | null;
  foods: FoodItem[];
  recipes: Recipe[];
  onChange: (item: MealItem | null) => void;
}

export default function MealSlot({ slotType, item, foods, recipes, onChange }: Props) {
  const [showRecipeSelector, setShowRecipeSelector] = useState(false);

  const current = item || emptyMealItem();

  const updateName = (name: string) => {
    onChange({ ...current, name });
  };

  const updateIngredient = (idx: number, field: keyof MealIngredient, value: string | number) => {
    const updated = [...current.ingredients];
    updated[idx] = { ...updated[idx], [field]: value };
    onChange({ ...current, ingredients: updated });
  };

  const addIngredient = () => {
    onChange({
      ...current,
      ingredients: [...current.ingredients, { food_name: '', amount_g: 0 }],
    });
  };

  const removeIngredient = (idx: number) => {
    const updated = current.ingredients.filter((_, i) => i !== idx);
    onChange({ ...current, ingredients: updated });
  };

  const handleRecipeSelect = (selected: MealItem) => {
    onChange(selected);
    setShowRecipeSelector(false);
  };

  const clearSlot = () => {
    onChange(null);
  };

  return (
    <div className="meal-slot">
      <div className="meal-slot-header">
        <span className="meal-slot-label">{MEAL_SLOT_LABELS[slotType]}</span>
        <div style={{ display: 'flex', gap: 4 }}>
          <button className="recipe-select-btn" onClick={() => setShowRecipeSelector(true)}>
            レシピ
          </button>
          {(item?.name || item?.ingredients.length) ? (
            <button className="recipe-select-btn" onClick={clearSlot} style={{ borderColor: '#e17055', color: '#e17055' }}>
              クリア
            </button>
          ) : null}
        </div>
      </div>

      <input
        className="dish-name-input"
        type="text"
        placeholder="料理名"
        value={current.name}
        onChange={e => updateName(e.target.value)}
      />

      {current.ingredients.map((ing, idx) => (
        <div key={idx} className="ingredient-row">
          <select
            value={ing.food_name}
            onChange={e => updateIngredient(idx, 'food_name', e.target.value)}
          >
            <option value="">食材を選択</option>
            {foods.map(f => (
              <option key={f.food_name} value={f.food_name}>{f.food_name}</option>
            ))}
          </select>
          <input
            type="number"
            min={0}
            step={1}
            value={ing.amount_g || ''}
            onChange={e => updateIngredient(idx, 'amount_g', Number(e.target.value))}
            placeholder="g"
          />
          <button className="remove-btn" onClick={() => removeIngredient(idx)}>&times;</button>
        </div>
      ))}

      <button className="add-ingredient-btn" onClick={addIngredient}>
        + 食材を追加
      </button>

      {showRecipeSelector && (
        <DishSelector
          recipes={recipes}
          onSelect={handleRecipeSelect}
          onClose={() => setShowRecipeSelector(false)}
        />
      )}
    </div>
  );
}
