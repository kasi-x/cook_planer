import type { FoodItem, FixedFood, OptimizeResult, OptimizeStrategy, ScoringParams, Gender, MealType, Recipe, DishCalculateResult } from './types';
import { DEFAULT_SCORING_PARAMS } from './types';

const API_BASE = '/api';

export async function fetchFoods(): Promise<FoodItem[]> {
  const response = await fetch(`${API_BASE}/foods`);
  if (!response.ok) {
    throw new Error('食材データの取得に失敗しました');
  }
  const data = await response.json();
  if (!Array.isArray(data) || data.length === 0) {
    throw new Error('食材データが空です。データベースを確認してください。');
  }
  return data;
}

export async function fetchRecipes(): Promise<Recipe[]> {
  const response = await fetch(`${API_BASE}/recipes`);
  if (!response.ok) {
    throw new Error('レシピデータの取得に失敗しました');
  }
  return response.json();
}

export async function fetchRecipe(recipeId: string): Promise<Recipe | null> {
  const response = await fetch(`${API_BASE}/recipes/${recipeId}`);
  if (!response.ok) {
    return null;
  }
  return response.json();
}

export interface DishIngredient {
  food_name: string;
  amount_g: number;
}

export async function calculateDish(
  ingredients: DishIngredient[],
  servings: number = 1
): Promise<DishCalculateResult> {
  const response = await fetch(`${API_BASE}/dish/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients, servings }),
  });
  if (!response.ok) {
    throw new Error('栄養計算に失敗しました');
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
