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

export type Gender = 'male' | 'female';

export interface AgeGroup {
  id: string;
  label: string;
  minAge: number;
  maxAge: number;
}

export const AGE_GROUPS: AgeGroup[] = [
  { id: '12-14', label: '12-14歳', minAge: 12, maxAge: 14 },
  { id: '15-17', label: '15-17歳', minAge: 15, maxAge: 17 },
  { id: '18-29', label: '18-29歳', minAge: 18, maxAge: 29 },
  { id: '30-49', label: '30-49歳', minAge: 30, maxAge: 49 },
  { id: '50-64', label: '50-64歳', minAge: 50, maxAge: 64 },
  { id: '65-74', label: '65-74歳', minAge: 65, maxAge: 74 },
];

export const GENDER_LABELS: Record<Gender, string> = {
  male: '男性',
  female: '女性',
};

export type MealType = 'daily' | 'per_meal' | 'school_lunch';

export const MEAL_TYPE_LABELS: Record<MealType, string> = {
  daily: '1日分',
  per_meal: '一食分',
  school_lunch: '給食基準（中学生）',
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
