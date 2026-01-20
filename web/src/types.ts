export interface FoodItem {
  food_name: string;
  price_per_100g: number;
  energy_kcal: number;
  protein_g: number;
}

export interface FixedFood {
  food_name: string;
  amount_g: number;
}

export type OptimizeStrategy = 'strict' | 'calorie_focused' | 'balanced' | 'custom_score';

export interface ScoringParams {
  deficit_penalty: number;
  cost_bonus: number;
  calorie_weight: number;
  protein_weight: number;
  vitamin_weight: number;
  mineral_weight: number;
}

export const DEFAULT_SCORING_PARAMS: ScoringParams = {
  deficit_penalty: 1.0,
  cost_bonus: 0.1,
  calorie_weight: 1.0,
  protein_weight: 1.0,
  vitamin_weight: 1.0,
  mineral_weight: 1.0,
};

export const STRATEGY_LABELS: Record<OptimizeStrategy, string> = {
  strict: '厳密モード（全栄養素必達）',
  calorie_focused: 'カロリー重視',
  balanced: 'バランス（デフォルト）',
  custom_score: 'カスタムスコア',
};

export interface FoodAmount {
  food_name: string;
  amount_g: number;
  cost: number;
  contribution_percent: number;
  source_price: string;
  source_nutrition: string;
}

export interface FoodContribution {
  food_name: string;
  amount: number;
  contribution: number;
  percentage: number;
}

export interface NutrientStatus {
  name: string;
  actual: number;
  required: number;
  unit: string;
  ratio: number;
  achieved: boolean;
  contributions: FoodContribution[];
}

export interface OptimizeResult {
  success: boolean;
  message: string;
  amounts: Record<string, number>;
  food_amounts: FoodAmount[];
  total_cost: number;
  daily_cost: number;
  monthly_cost: number;
  nutrients: NutrientStatus[];
}
