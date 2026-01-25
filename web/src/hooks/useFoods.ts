import { useState, useEffect, useCallback } from 'react';
import type { FoodItem, FixedFood, OptimizeResult, OptimizeStrategy, ScoringParams, Gender, MealType } from '../types';
import { DEFAULT_SCORING_PARAMS } from '../types';
import { fetchFoods, runOptimize } from '../api';
import type { Preset } from '../components/PresetSelector';

export function useFoods() {
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [selectedFoods, setSelectedFoods] = useState<Set<string>>(new Set());
  const [fixedFoods, setFixedFoods] = useState<Map<string, number>>(new Map());
  const [strategy, setStrategy] = useState<OptimizeStrategy>('balanced');
  const [scoringParams, setScoringParams] = useState<ScoringParams>(DEFAULT_SCORING_PARAMS);
  const [age, setAge] = useState<number>(23);
  const [gender, setGender] = useState<Gender>('male');
  const [mealType, setMealType] = useState<MealType>('daily');
  const [result, setResult] = useState<OptimizeResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  useEffect(() => {
    fetchFoods()
      .then(setFoods)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const toggleFood = useCallback((name: string) => {
    setSelectedFoods((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  }, []);

  const setFixedAmount = useCallback((name: string, amount: number | null) => {
    setFixedFoods((prev) => {
      const next = new Map(prev);
      if (amount === null || amount <= 0) {
        next.delete(name);
      } else {
        next.set(name, amount);
        // 固定された食品は選択から外す
        setSelectedFoods((prevSelected) => {
          const newSelected = new Set(prevSelected);
          newSelected.delete(name);
          return newSelected;
        });
      }
      return next;
    });
  }, []);

  const selectAll = useCallback(() => {
    setSelectedFoods(new Set(foods.map((f) => f.food_name)));
  }, [foods]);

  const clearAll = useCallback(() => {
    setSelectedFoods(new Set());
    setFixedFoods(new Map());
  }, []);

  const applyRecipe = useCallback((recipeFoods: { name: string; amount: number }[]) => {
    // 利用可能な食品名のセットを作成
    const availableFoodNames = new Set(foods.map(f => f.food_name));

    // 不足している食品を追跡
    const missingFoods: string[] = [];

    // レシピの食品を固定食品として設定
    const newFixedFoods = new Map<string, number>();
    for (const { name, amount } of recipeFoods) {
      if (availableFoodNames.has(name)) {
        newFixedFoods.set(name, amount);
      } else {
        missingFoods.push(name);
      }
    }
    setFixedFoods(newFixedFoods);

    // 選択食品はクリア
    setSelectedFoods(new Set());

    // 不足食品がある場合は警告を表示
    if (missingFoods.length > 0) {
      setWarning(`一部の食品がデータベースにありません: ${missingFoods.slice(0, 3).join(', ')}${missingFoods.length > 3 ? ` 他${missingFoods.length - 3}件` : ''}`);
    } else {
      setWarning(null);
    }
    setError(null);
  }, [foods]);

  const applyPreset = useCallback((preset: Preset) => {
    // 利用可能な食品名のセットを作成
    const availableFoodNames = new Set(foods.map(f => f.food_name));

    // 不足している食品を追跡
    const missingFoods: string[] = [];

    // 固定食品を設定
    const newFixedFoods = new Map<string, number>();
    for (const { name, amount } of preset.fixedFoods) {
      if (availableFoodNames.has(name)) {
        newFixedFoods.set(name, amount);
      } else {
        missingFoods.push(name);
      }
    }
    setFixedFoods(newFixedFoods);

    // 選択食品を設定（固定食品は除外）
    const newSelectedFoods = new Set<string>();
    for (const name of preset.selectedFoods) {
      if (availableFoodNames.has(name) && !newFixedFoods.has(name)) {
        newSelectedFoods.add(name);
      } else if (!availableFoodNames.has(name)) {
        missingFoods.push(name);
      }
    }
    setSelectedFoods(newSelectedFoods);

    // 年齢・性別・食事タイプを設定
    if (preset.age !== undefined) setAge(preset.age);
    if (preset.gender !== undefined) setGender(preset.gender);
    if (preset.mealType !== undefined) setMealType(preset.mealType);

    // 不足食品がある場合は警告を表示
    if (missingFoods.length > 0) {
      setWarning(`一部の食品がデータベースにありません: ${missingFoods.slice(0, 3).join(', ')}${missingFoods.length > 3 ? ` 他${missingFoods.length - 3}件` : ''}`);
    } else {
      setWarning(null);
    }
    setError(null);
  }, [foods]);

  const optimize = useCallback(async () => {
    if (selectedFoods.size === 0 && fixedFoods.size === 0) {
      setError('食材を選択してください');
      return;
    }

    setOptimizing(true);
    setError(null);

    try {
      const fixedFoodsArray: FixedFood[] = Array.from(fixedFoods.entries()).map(
        ([food_name, amount_g]) => ({ food_name, amount_g })
      );
      const res = await runOptimize(
        Array.from(selectedFoods),
        fixedFoodsArray,
        1500,
        strategy,
        scoringParams,
        age,
        gender,
        mealType
      );
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : '最適化に失敗しました');
    } finally {
      setOptimizing(false);
    }
  }, [selectedFoods, fixedFoods, strategy, scoringParams, age, gender, mealType]);

  return {
    foods,
    selectedFoods,
    fixedFoods,
    strategy,
    scoringParams,
    age,
    gender,
    mealType,
    result,
    loading,
    optimizing,
    error,
    warning,
    toggleFood,
    setFixedAmount,
    setStrategy,
    setScoringParams,
    setAge,
    setGender,
    setMealType,
    selectAll,
    clearAll,
    applyPreset,
    applyRecipe,
    optimize,
  };
}
