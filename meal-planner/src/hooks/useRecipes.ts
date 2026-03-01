import { useState, useEffect, useCallback } from 'react';
import type { FoodItem, Recipe } from '../types';
import * as api from '../api';

export function useRecipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [loading, setLoading] = useState(false);

  const loadRecipes = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.fetchRecipes();
      setRecipes(data);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFoods = useCallback(async () => {
    const data = await api.fetchFoods();
    setFoods(data);
  }, []);

  useEffect(() => {
    loadRecipes();
    loadFoods();
  }, [loadRecipes, loadFoods]);

  return { recipes, foods, loading, loadRecipes };
}
