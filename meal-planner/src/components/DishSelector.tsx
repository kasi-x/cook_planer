import { useState, useMemo } from 'react';
import type { Recipe, MealItem } from '../types';

interface Props {
  recipes: Recipe[];
  onSelect: (item: MealItem) => void;
  onClose: () => void;
}

export default function DishSelector({ recipes, onSelect, onClose }: Props) {
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    if (!query) return recipes;
    const q = query.toLowerCase();
    return recipes.filter(r => r.name.toLowerCase().includes(q));
  }, [recipes, query]);

  const handleSelect = (recipe: Recipe) => {
    const item: MealItem = {
      name: recipe.name,
      recipe_id: recipe.id,
      ingredients: recipe.ingredients
        .filter(ing => ing.matched_food && ing.amount_g)
        .map(ing => ({
          food_name: ing.matched_food!,
          amount_g: (ing.amount_g! / recipe.servings),
        })),
    };
    onSelect(item);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: 500 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>レシピから選択</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="dish-selector">
          <input
            className="search-input"
            type="text"
            placeholder="レシピ名で検索..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            autoFocus
          />
          <div className="recipe-list">
            {filtered.length === 0 && (
              <p style={{ color: '#636e72', fontSize: 13, textAlign: 'center', padding: 20 }}>
                該当するレシピがありません
              </p>
            )}
            {filtered.map(r => (
              <div key={r.id} className="recipe-item" onClick={() => handleSelect(r)}>
                <div className="recipe-name">{r.name}</div>
                <div className="recipe-ingredients">
                  {r.ingredients.slice(0, 4).map(i => i.original_name).join('、')}
                  {r.ingredients.length > 4 && '...'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
