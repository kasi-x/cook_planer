export interface FoodItem {
  food_name: string;
  price_per_100g: number;
  energy_kcal: number;
  protein_g: number;
}

export interface NutrientStatus {
  name: string;
  actual: number;
  required: number;
  unit: string;
  ratio: number;
  achieved: boolean;
}

export interface OptimizeResult {
  success: boolean;
  message: string;
  amounts: Record<string, number>;
  total_cost: number;
  daily_cost: number;
  monthly_cost: number;
  nutrients: NutrientStatus[];
}
