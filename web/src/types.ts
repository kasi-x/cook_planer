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

// Recipe types
export interface RecipeIngredient {
  original_name: string;
  amount_text: string;
  amount_g: number | null;
  matched_food: string | null;
}

export interface Recipe {
  id: string;
  name: string;
  servings: number;
  ingredients: RecipeIngredient[];
}

// Dish calculator types
export interface DishNutrition {
  name: string;
  value: number;
  unit: string;
}

export interface DishCalculateResult {
  success: boolean;
  message: string;
  total_cost: number;
  per_serving_cost: number;
  nutrients: DishNutrition[];
}

// Food categories for filtering
export type FoodCategory =
  | 'meat'       // 肉類
  | 'fish'       // 魚介類
  | 'egg_dairy'  // 卵・乳製品
  | 'soy'        // 豆類
  | 'vegetable'  // 野菜
  | 'mushroom'   // きのこ
  | 'grain'      // 穀類
  | 'fruit'      // 果物
  | 'seaweed'    // 海藻
  | 'seasoning'  // 調味料
  | 'other';     // その他

export const FOOD_CATEGORY_LABELS: Record<FoodCategory, string> = {
  meat: '肉類',
  fish: '魚介類',
  egg_dairy: '卵・乳製品',
  soy: '豆類',
  vegetable: '野菜',
  mushroom: 'きのこ',
  grain: '穀類',
  fruit: '果物',
  seaweed: '海藻',
  seasoning: '調味料',
  other: 'その他',
};

// Categorize food by name
export function categorizeFood(foodName: string): FoodCategory {
  // 肉類
  if (/鶏|豚|牛|肉|ハム|ベーコン|ソーセージ/.test(foodName)) return 'meat';
  // 魚介類
  if (/さけ|さば|あじ|いわし|まぐろ|たら|えび|いか|魚/.test(foodName)) return 'fish';
  // 卵・乳製品
  if (/卵|牛乳|ヨーグルト|チーズ|バター/.test(foodName)) return 'egg_dairy';
  // 豆類
  if (/豆腐|納豆|豆乳|油揚げ|厚揚げ|大豆/.test(foodName)) return 'soy';
  // きのこ
  if (/しいたけ|えのき|しめじ|まいたけ|エリンギ|きのこ/.test(foodName)) return 'mushroom';
  // 穀類
  if (/米|パン|麺|うどん|そば|パスタ/.test(foodName)) return 'grain';
  // 果物
  if (/バナナ|りんご|みかん|キウイ|いちご|果/.test(foodName)) return 'fruit';
  // 海藻
  if (/わかめ|ひじき|のり|昆布|海藻/.test(foodName)) return 'seaweed';
  // 調味料
  if (/味噌|醤油|塩|砂糖|酢|油/.test(foodName)) return 'seasoning';
  // 野菜（デフォルト）
  if (/キャベツ|にんじん|たまねぎ|ほうれん|ブロッコリー|だいこん|じゃがいも|もやし|トマト|レタス|きゅうり|ねぎ|ごぼう|れんこん|なす|ピーマン|はくさい|かぼちゃ|こまつな|みずな/.test(foodName)) return 'vegetable';

  return 'other';
}
