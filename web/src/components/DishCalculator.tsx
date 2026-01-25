import { useState } from 'react';
import type { FoodItem, DishCalculateResult } from '../types';
import { calculateDish } from '../api';

interface DishIngredient {
  food_name: string;
  amount_g: number;
}

interface Props {
  foods: FoodItem[];
}

export function DishCalculator({ foods }: Props) {
  const [ingredients, setIngredients] = useState<DishIngredient[]>([]);
  const [servings, setServings] = useState(1);
  const [result, setResult] = useState<DishCalculateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleAddIngredient = (foodName: string) => {
    if (!foodName) return;
    if (ingredients.some((i) => i.food_name === foodName)) return;

    setIngredients([...ingredients, { food_name: foodName, amount_g: 100 }]);
    setSearchQuery('');
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
    setResult(null);
  };

  const handleAmountChange = (index: number, amount: number) => {
    const updated = [...ingredients];
    updated[index].amount_g = Math.max(1, amount);
    setIngredients(updated);
  };

  const handleCalculate = async () => {
    if (ingredients.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const data = await calculateDish(ingredients, servings);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : '計算に失敗しました');
      setResult(null);
    }
    setLoading(false);
  };

  const handleClear = () => {
    setIngredients([]);
    setResult(null);
    setError(null);
  };

  const filteredFoods = searchQuery
    ? foods.filter((f) =>
        f.food_name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : foods;

  const totalWeight = ingredients.reduce((sum, i) => sum + i.amount_g, 0);

  return (
    <section className="panel dish-calculator">
      <h2>一品計算機</h2>
      <p className="hint">食材と量を入力して栄養価を計算</p>

      <button
        type="button"
        className="btn-toggle"
        onClick={() => setShowForm(!showForm)}
      >
        {showForm ? '閉じる' : '計算機を開く'}
      </button>

      {showForm && (
        <div className="calculator-form">
          <div className="ingredient-input">
            <input
              type="text"
              placeholder="食材を検索して追加..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <div className="search-dropdown">
                {filteredFoods.slice(0, 8).map((food) => (
                  <button
                    key={food.food_name}
                    type="button"
                    className="search-item"
                    onClick={() => handleAddIngredient(food.food_name)}
                    disabled={ingredients.some((i) => i.food_name === food.food_name)}
                  >
                    {food.food_name}
                    <span className="food-price">¥{food.price_per_100g}/100g</span>
                  </button>
                ))}
                {filteredFoods.length === 0 && (
                  <div className="no-results">該当する食材がありません</div>
                )}
              </div>
            )}
          </div>

          {ingredients.length > 0 && (
            <div className="ingredient-list">
              <h4>食材リスト ({ingredients.length}品, 計{totalWeight}g):</h4>
              <ul>
                {ingredients.map((ing, idx) => (
                  <li key={ing.food_name}>
                    <span className="ing-name">{ing.food_name}</span>
                    <input
                      type="number"
                      min={1}
                      value={ing.amount_g}
                      onChange={(e) =>
                        handleAmountChange(idx, Number(e.target.value))
                      }
                    />
                    <span>g</span>
                    <button
                      type="button"
                      className="btn-remove"
                      onClick={() => handleRemoveIngredient(idx)}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>

              <div className="servings-input">
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
              </div>

              <div className="calculator-actions">
                <button
                  type="button"
                  className="btn-calculate"
                  onClick={handleCalculate}
                  disabled={loading}
                >
                  {loading ? '計算中...' : '栄養価を計算'}
                </button>
                <button
                  type="button"
                  className="btn-clear"
                  onClick={handleClear}
                >
                  クリア
                </button>
              </div>
            </div>
          )}

          {error && <div className="dish-error">{error}</div>}

          {result && result.success && (
            <div className="dish-result">
              <h4>計算結果</h4>
              <div className="cost-info">
                <span>総コスト: ¥{result.total_cost}</span>
                <span>1人分: ¥{result.per_serving_cost}</span>
              </div>
              <table className="nutrient-table">
                <thead>
                  <tr>
                    <th>栄養素</th>
                    <th>総量</th>
                    <th>1人分</th>
                  </tr>
                </thead>
                <tbody>
                  {result.nutrients.map((n) => (
                    <tr key={n.name}>
                      <td>{n.name}</td>
                      <td>
                        {n.value}
                        {n.unit}
                      </td>
                      <td>
                        {Math.round((n.value / servings) * 10) / 10}
                        {n.unit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
