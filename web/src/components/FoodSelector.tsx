import { useState, useMemo } from 'react';
import type { FoodItem, FoodCategory } from '../types';
import { categorizeFood, FOOD_CATEGORY_LABELS } from '../types';

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
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<FoodCategory | 'all'>('all');

  // Group foods by category
  const foodsByCategory = useMemo(() => {
    const grouped: Record<FoodCategory, FoodItem[]> = {
      meat: [],
      fish: [],
      egg_dairy: [],
      soy: [],
      vegetable: [],
      mushroom: [],
      grain: [],
      fruit: [],
      seaweed: [],
      seasoning: [],
      other: [],
    };

    for (const food of foods) {
      const category = categorizeFood(food.food_name);
      grouped[category].push(food);
    }

    return grouped;
  }, [foods]);

  // Get category counts
  const categoryCounts = useMemo(() => {
    const counts: Record<FoodCategory | 'all', number> = { all: foods.length } as any;
    for (const [cat, items] of Object.entries(foodsByCategory)) {
      counts[cat as FoodCategory] = items.length;
    }
    return counts;
  }, [foods, foodsByCategory]);

  // Filter foods
  const filteredFoods = useMemo(() => {
    let result = foods;

    // Category filter
    if (selectedCategory !== 'all') {
      result = foodsByCategory[selectedCategory];
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter((f) =>
        f.food_name.toLowerCase().includes(query)
      );
    }

    return result;
  }, [foods, foodsByCategory, selectedCategory, searchQuery]);

  const handleFixClick = (foodName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const currentAmount = fixedFoods.get(foodName);
    setInputValue(currentAmount ? currentAmount.toString() : '100');
    setEditingFood(foodName);
  };

  const handleFixSubmit = (foodName: string, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const amount = parseFloat(inputValue);
    onSetFixed(foodName, isNaN(amount) || amount <= 0 ? null : amount);
    setEditingFood(null);
    setInputValue('');
  };

  const handleRemoveFixed = (foodName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onSetFixed(foodName, null);
  };

  const totalSelected = selectedFoods.size + fixedFoods.size;

  // Categories to show (only ones with items)
  const visibleCategories = (Object.keys(FOOD_CATEGORY_LABELS) as FoodCategory[]).filter(
    (cat) => categoryCounts[cat] > 0
  );

  return (
    <section className="panel food-selector-panel">
      <h2>食材選択</h2>

      {/* Search box */}
      <div className="search-box">
        <input
          type="text"
          placeholder="食材を検索..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchQuery && (
          <button
            type="button"
            className="clear-search"
            onClick={() => setSearchQuery('')}
          >
            ×
          </button>
        )}
      </div>

      {/* Category tabs */}
      <div className="category-tabs">
        <button
          type="button"
          className={`category-tab ${selectedCategory === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('all')}
        >
          すべて ({categoryCounts.all})
        </button>
        {visibleCategories.map((cat) => (
          <button
            key={cat}
            type="button"
            className={`category-tab ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {FOOD_CATEGORY_LABELS[cat]} ({categoryCounts[cat]})
          </button>
        ))}
      </div>

      {/* Action buttons */}
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

      {/* Food list */}
      <ul className="food-list">
        {filteredFoods.length === 0 ? (
          <li className="no-results">該当する食材がありません</li>
        ) : (
          filteredFoods.map((food) => {
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
                      ¥{food.price_per_100g.toFixed(0)}/100g
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
                        min={1}
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
          })
        )}
      </ul>
    </section>
  );
}
