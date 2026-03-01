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

export interface MealIngredient {
  food_name: string;
  amount_g: number;
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
