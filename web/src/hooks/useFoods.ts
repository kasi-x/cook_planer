import { useState, useEffect, useCallback } from 'react';
import type { FoodItem, OptimizeResult } from '../types';
import { fetchFoods, runOptimize } from '../api';

export function useFoods() {
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [selectedFoods, setSelectedFoods] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<OptimizeResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const selectAll = useCallback(() => {
    setSelectedFoods(new Set(foods.map((f) => f.food_name)));
  }, [foods]);

  const clearAll = useCallback(() => {
    setSelectedFoods(new Set());
  }, []);

  const optimize = useCallback(async () => {
    if (selectedFoods.size === 0) {
      setError('食材を選択してください');
      return;
    }

    setOptimizing(true);
    setError(null);

    try {
      const res = await runOptimize(Array.from(selectedFoods));
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : '最適化に失敗しました');
    } finally {
      setOptimizing(false);
    }
  }, [selectedFoods]);

  return {
    foods,
    selectedFoods,
    result,
    loading,
    optimizing,
    error,
    toggleFood,
    selectAll,
    clearAll,
    optimize,
  };
}
