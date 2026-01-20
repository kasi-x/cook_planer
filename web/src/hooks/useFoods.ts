import { useState, useEffect, useCallback } from 'react';
import type { FoodItem, FixedFood, OptimizeResult, OptimizeStrategy, ScoringParams } from '../types';
import { DEFAULT_SCORING_PARAMS } from '../types';
import { fetchFoods, runOptimize } from '../api';

export function useFoods() {
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [selectedFoods, setSelectedFoods] = useState<Set<string>>(new Set());
  const [fixedFoods, setFixedFoods] = useState<Map<string, number>>(new Map());
  const [strategy, setStrategy] = useState<OptimizeStrategy>('balanced');
  const [scoringParams, setScoringParams] = useState<ScoringParams>(DEFAULT_SCORING_PARAMS);
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

  const setFixedAmount = useCallback((name: string, amount: number | null) => {
    console.log('setFixedAmount called:', name, amount);
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
      console.log('fixedFoods after update:', Array.from(next.entries()));
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
      console.log('Optimizing with:', {
        selectedFoods: Array.from(selectedFoods),
        fixedFoods: fixedFoodsArray,
        strategy,
        scoringParams,
      });
      const res = await runOptimize(
        Array.from(selectedFoods),
        fixedFoodsArray,
        1500,
        strategy,
        scoringParams
      );
      console.log('Optimization result:', res);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : '最適化に失敗しました');
    } finally {
      setOptimizing(false);
    }
  }, [selectedFoods, fixedFoods, strategy, scoringParams]);

  return {
    foods,
    selectedFoods,
    fixedFoods,
    strategy,
    scoringParams,
    result,
    loading,
    optimizing,
    error,
    toggleFood,
    setFixedAmount,
    setStrategy,
    setScoringParams,
    selectAll,
    clearAll,
    optimize,
  };
}
