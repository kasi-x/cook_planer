import { useState, useEffect } from 'react';
import type { Recipe } from '../types';
import { fetchRecipes } from '../api';

interface Props {
  onApplyRecipe: (foods: { name: string; amount: number }[]) => void;
}

export function RecipeSelector({ onApplyRecipe }: Props) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [servings, setServings] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecipes()
      .then((data) => {
        setRecipes(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || 'レシピの読み込みに失敗しました');
        setLoading(false);
      });
  }, []);

  const handleRecipeSelect = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setServings(recipe.servings);
  };

  const handleApply = () => {
    if (!selectedRecipe) return;

    const ratio = servings / selectedRecipe.servings;
    const foods: { name: string; amount: number }[] = [];

    for (const ing of selectedRecipe.ingredients) {
      if (ing.matched_food && ing.amount_g) {
        foods.push({
          name: ing.matched_food,
          amount: Math.round(ing.amount_g * ratio),
        });
      }
    }

    onApplyRecipe(foods);
    setSelectedRecipe(null);
  };

  const filteredRecipes = recipes.filter((r) =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const matchedCount = selectedRecipe
    ? selectedRecipe.ingredients.filter((i) => i.matched_food).length
    : 0;
  const totalCount = selectedRecipe?.ingredients.length || 0;

  if (loading) {
    return (
      <section className="panel recipe-selector">
        <h2>レシピから選ぶ</h2>
        <div className="loading-spinner">読み込み中...</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel recipe-selector">
        <h2>レシピから選ぶ</h2>
        <div className="error-message">
          <p>{error}</p>
          <button
            type="button"
            className="btn-retry"
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchRecipes()
                .then(setRecipes)
                .catch((e) => setError(e.message))
                .finally(() => setLoading(false));
            }}
          >
            再試行
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="panel recipe-selector">
      <h2>レシピから選ぶ</h2>
      <p className="hint">料理を選ぶと食材が自動入力されます</p>

      {!selectedRecipe ? (
        <>
          <div className="search-box">
            <input
              type="text"
              placeholder="レシピを検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="recipe-grid">
            {filteredRecipes.map((recipe) => (
              <button
                key={recipe.id}
                type="button"
                className="recipe-btn"
                onClick={() => handleRecipeSelect(recipe)}
              >
                <span className="recipe-name">{recipe.name}</span>
                <span className="recipe-servings">{recipe.servings}人分</span>
              </button>
            ))}
            {filteredRecipes.length === 0 && (
              <div className="no-results">該当するレシピがありません</div>
            )}
          </div>
        </>
      ) : (
        <div className="recipe-detail">
          <h3>{selectedRecipe.name}</h3>

          {matchedCount < totalCount && (
            <div className="match-warning">
              {totalCount - matchedCount}個の食材がデータベースにありません
            </div>
          )}

          <div className="servings-control">
            <label>
              人数:
              <input
                type="number"
                min={1}
                max={10}
                value={servings}
                onChange={(e) => setServings(Math.max(1, Math.min(10, Number(e.target.value))))}
              />
              人分
            </label>
            <span className="servings-hint">
              (元レシピ: {selectedRecipe.servings}人分)
            </span>
          </div>

          <div className="ingredient-list">
            <h4>食材 ({matchedCount}/{totalCount}):</h4>
            <ul>
              {selectedRecipe.ingredients.map((ing, idx) => {
                const ratio = servings / selectedRecipe.servings;
                const adjustedAmount = ing.amount_g
                  ? Math.round(ing.amount_g * ratio)
                  : null;

                return (
                  <li key={idx} className={ing.matched_food ? '' : 'unmatched'}>
                    <span className="ing-name">{ing.original_name}</span>
                    <span className="ing-amount">
                      {adjustedAmount ? `${adjustedAmount}g` : ing.amount_text}
                    </span>
                    {ing.matched_food ? (
                      <span className="ing-matched">
                        ({ing.matched_food})
                      </span>
                    ) : (
                      <span className="ing-unmatched">(未対応)</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="recipe-actions">
            <button
              type="button"
              className="btn-apply"
              onClick={handleApply}
              disabled={matchedCount === 0}
            >
              この食材を使う ({matchedCount}品)
            </button>
            <button
              type="button"
              className="btn-cancel"
              onClick={() => setSelectedRecipe(null)}
            >
              戻る
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
