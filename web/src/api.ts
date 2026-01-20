import type { FoodItem, FixedFood, OptimizeResult, OptimizeStrategy, ScoringParams, Gender, MealType } from './types';
import { DEFAULT_SCORING_PARAMS } from './types';

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
  fixedFoods: FixedFood[] = [],
  maxFoodAmountG: number = 1500,
  strategy: OptimizeStrategy = 'balanced',
  scoringParams: ScoringParams = DEFAULT_SCORING_PARAMS,
  age: number = 23,
  gender: Gender = 'male',
  mealType: MealType = 'daily'
): Promise<OptimizeResult> {
  const response = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_foods: selectedFoods,
      max_food_amount_g: maxFoodAmountG,
      fixed_foods: fixedFoods,
      strategy: strategy,
      scoring_params: scoringParams,
      age: age,
      gender: gender,
      meal_type: mealType,
    }),
  });
  if (!response.ok) {
    throw new Error('最適化リクエストに失敗しました');
  }
  return response.json();
}
