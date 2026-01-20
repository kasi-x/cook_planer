import type { FoodItem, OptimizeResult } from './types';

const API_BASE = '/api';

export async function fetchFoods(): Promise<FoodItem[]> {
  const response = await fetch(`${API_BASE}/foods`);
  if (!response.ok) {
    throw new Error('食材データの取得に失敗しました');
  }
  return response.json();
}

export async function runOptimize(
  selectedFoods: string[],
  maxFoodAmountG: number = 1500
): Promise<OptimizeResult> {
  const response = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_foods: selectedFoods,
      max_food_amount_g: maxFoodAmountG,
    }),
  });
  if (!response.ok) {
    throw new Error('最適化リクエストに失敗しました');
  }
  return response.json();
}
