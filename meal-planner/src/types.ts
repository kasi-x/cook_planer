export type SchoolGradeLevel =
  | 'elementary_low'
  | 'elementary_mid'
  | 'elementary_high'
  | 'junior_high';

export const GRADE_LABELS: Record<SchoolGradeLevel, string> = {
  elementary_low: '小学校低学年',
  elementary_mid: '小学校中学年',
  elementary_high: '小学校高学年',
  junior_high: '中学校',
};

export type MealSlotType = 'staple' | 'main_dish' | 'side_dish' | 'soup' | 'dessert';

export const MEAL_SLOT_LABELS: Record<MealSlotType, string> = {
  staple: '主食',
  main_dish: '主菜',
  side_dish: '副菜',
  soup: '汁物',
  dessert: 'デザート',
};

export type CookingMethod = '生' | 'ゆで' | '焼き' | '揚げ' | '蒸し' | '炒め';

export const COOKING_METHOD_LABELS: Record<CookingMethod, string> = {
  '生': '生',
  'ゆで': 'ゆで',
  '焼き': '焼き',
  '揚げ': '揚げ',
  '蒸し': '蒸し',
  '炒め': '炒め',
};

export interface MealIngredient {
  food_name: string;
  amount_g: number;
  cooking_method?: CookingMethod;
}

export interface MealItem {
  name: string;
  recipe_id: string | null;
  ingredients: MealIngredient[];
}

export interface DailyMenuData {
  staple: MealItem | null;
  main_dish: MealItem | null;
  side_dish: MealItem | null;
  soup: MealItem | null;
  dessert: MealItem | null;
  milk: boolean;
}

export interface MenuPlan {
  id: number;
  name: string;
  grade_level: SchoolGradeLevel;
  start_date: string;
  end_date: string;
  created_at: string;
  allergen_profile: string[];
}

export interface DailyMenu {
  plan_id: number;
  date: string;
  menu: DailyMenuData;
}

export interface NutrientResult {
  key: string;
  name: string;
  unit: string;
  actual: number;
  standard: number;
  ratio: number;
}

export interface DailyNutritionResult {
  date: string;
  total_cost: number;
  nutrients: NutrientResult[];
  achievement_rate: number;
}

export interface WeeklyNutritionResult {
  start_date: string;
  end_date: string;
  daily_results: DailyNutritionResult[];
  weekly_average: NutrientResult[];
  total_cost: number;
  average_achievement_rate: number;
}

export interface FoodItem {
  food_name: string;
  price_per_100g: number;
  energy_kcal: number;
  protein_g: number;
}

export interface Recipe {
  id: string;
  name: string;
  servings: number;
  source_url: string | null;
  ingredients: RecipeIngredient[];
}

export interface RecipeIngredient {
  original_name: string;
  amount_text: string;
  amount_g: number | null;
  matched_food: string | null;
}

export interface NutritionStandard {
  key: string;
  name: string;
  unit: string;
  value: number;
}

// --- F1: 季節の食べもの ---
export interface SeasonalFood {
  name: string;
  category: string;
  seasonal_factor: number;
  quarter: string;
  quarter_label: string;
  in_season: boolean;
}

export interface SeasonalRecommendation {
  seasonal_ratio: number;
  seasonal_items: { name: string; category: string; seasonal_factor: number }[];
  non_seasonal_items: { name: string; category: string; seasonal_factor: number }[];
  suggestions: string[];
}

// --- F2: アレルギー管理 ---
export interface AllergenInfo {
  id: string;
  name: string;
  category: 'mandatory' | 'recommended';
  category_label: string;
}

export interface AllergenWarning {
  allergen: string;
  severity: string;
  source_food: string;
  slot: string;
}

// --- F4/F5: 価格予測・バッファー ---
export interface PricePrediction {
  food_name: string;
  base_price: number;
  predicted_price: number;
  confidence: number;
  trend_direction: string;
  seasonal_factor?: number;
}

export interface MenuCostEstimate {
  total_cost: number;
  buffered_total_cost: number;
  buffer_pct: number;
  items: {
    food_name: string;
    amount_g: number;
    predicted_price_per_100g: number;
    cost: number;
    buffered_price_per_100g?: number;
    buffered_cost?: number;
    slot: string;
  }[];
  month: number;
}

// --- F6: サブプラン ---
export interface SubPlan {
  id: number;
  parent_plan_id: number;
  name: string;
  description: string;
  excluded_allergens: string[];
  created_at: string;
}

// --- F7: 食べ合わせ ---
export interface CombinationResult {
  good_effects: {
    type: string;
    nutrients: string[];
    foods: Record<string, string[]>;
    description: string;
  }[];
  bad_effects: {
    type: string;
    nutrients: string[];
    foods: Record<string, string[]>;
    description: string;
    note?: string;
  }[];
  suggestions: string[];
}

// --- F8: 調理工数 ---
export interface CookingEffortResult {
  total_minutes: number;
  parallel_minutes: number;
  prep_minutes: number;
  cook_minutes: number;
  difficulty: number;
  difficulty_label: string;
  slots_detail: {
    slot: string;
    slot_label: string;
    dish_name: string;
    method: string;
    prep_minutes: number;
    cook_minutes: number;
    total_minutes: number;
    difficulty: number;
    ingredient_count: number;
  }[];
  suggestions: {
    slot: string;
    dish_name: string;
    suggestion: string;
    time_saved: number;
  }[];
}

/** 日付文字列 (YYYY-MM-DD) から月 (1-12) を取得 */
export function getMonthFromDate(dateStr: string): number {
  return new Date(dateStr + 'T00:00:00').getMonth() + 1;
}

/** 月→四半期マッピング（季節係数の静的判定用） */
const MONTH_TO_QUARTER: Record<number, string> = {
  4: 'Q1_Apr', 5: 'Q1_Apr', 6: 'Q1_Apr',
  7: 'Q2_Jul', 8: 'Q2_Jul', 9: 'Q2_Jul',
  10: 'Q3_Oct', 11: 'Q3_Oct', 12: 'Q3_Oct',
  1: 'Q4_Jan', 2: 'Q4_Jan', 3: 'Q4_Jan',
};

/** 旬カテゴリの季節係数（サーバー側 SEASONAL_FACTORS の軽量版） */
const SEASONAL_CATEGORY_MAP: Record<string, string> = {
  'だいこん': '野菜', 'にんじん': '野菜', 'キャベツ': '野菜', 'ほうれんそう': '野菜',
  'こまつな': '野菜', 'ブロッコリー': '野菜', 'トマト': '野菜', 'きゅうり': '野菜',
  'なす': '野菜', 'ピーマン': '野菜', 'かぼちゃ': '野菜', 'じゃがいも': '野菜',
  'さつまいも': '野菜', 'たまねぎ': '野菜', 'はくさい': '野菜', 'ねぎ': '野菜',
  'さけ': '魚介類', 'さば': '魚介類', 'あじ': '魚介類', 'いわし': '魚介類',
  'さんま': '魚介類', 'えび': '魚介類',
  'バナナ': '果物', 'りんご': '果物', 'みかん': '果物', 'キウイ': '果物',
};

/** カテゴリ×四半期の季節係数 (<1.0 = 旬) */
const SEASONAL_FACTORS: Record<string, Record<string, number>> = {
  '野菜': { 'Q1_Apr': 0.95, 'Q2_Jul': 0.9, 'Q3_Oct': 0.85, 'Q4_Jan': 1.1 },
  '魚介類': { 'Q1_Apr': 1.0, 'Q2_Jul': 1.05, 'Q3_Oct': 0.9, 'Q4_Jan': 0.95 },
  '果物': { 'Q1_Apr': 1.0, 'Q2_Jul': 0.9, 'Q3_Oct': 0.85, 'Q4_Jan': 1.1 },
};

/** 献立内に旬の食材があるかを静的に判定（API不要） */
export function hasSeasonalIngredients(menu: DailyMenuData, month: number): boolean {
  const quarter = MONTH_TO_QUARTER[month] || 'Q1_Apr';
  const slots = [menu.staple, menu.main_dish, menu.side_dish, menu.soup, menu.dessert];
  for (const slot of slots) {
    if (!slot) continue;
    for (const ing of slot.ingredients) {
      if (!ing.food_name) continue;
      for (const [keyword, category] of Object.entries(SEASONAL_CATEGORY_MAP)) {
        if (ing.food_name.includes(keyword)) {
          const factor = SEASONAL_FACTORS[category]?.[quarter] ?? 1.0;
          if (factor < 1.0) return true;
        }
      }
    }
  }
  return false;
}

export function emptyMenu(): DailyMenuData {
  return {
    staple: null,
    main_dish: null,
    side_dish: null,
    soup: null,
    dessert: null,
    milk: true,
  };
}

export function emptyMealItem(name: string = ''): MealItem {
  return { name, recipe_id: null, ingredients: [] };
}

export function getMenuSlotNames(menu: DailyMenuData): string[] {
  const names: string[] = [];
  if (menu.staple?.name) names.push(menu.staple.name);
  if (menu.main_dish?.name) names.push(menu.main_dish.name);
  if (menu.side_dish?.name) names.push(menu.side_dish.name);
  if (menu.soup?.name) names.push(menu.soup.name);
  if (menu.dessert?.name) names.push(menu.dessert.name);
  return names;
}
