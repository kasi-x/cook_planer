import type {
  MenuPlan,
  DailyMenu,
  DailyMenuData,
  DailyNutritionResult,
  WeeklyNutritionResult,
  FoodItem,
  Recipe,
  SchoolGradeLevel,
  SeasonalFood,
  SeasonalRecommendation,
  AllergenInfo,
  AllergenWarning,
  MenuCostEstimate,
  SubPlan,
  CombinationResult,
  CookingEffortResult,
} from './types';

const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// --- Menu Plans ---

export function fetchMenuPlans(): Promise<MenuPlan[]> {
  return fetchJSON(`${BASE}/menus`);
}

export function createMenuPlan(data: {
  name: string;
  grade_level: SchoolGradeLevel;
  start_date: string;
  end_date: string;
}): Promise<MenuPlan> {
  return fetchJSON(`${BASE}/menus`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateMenuPlan(
  planId: number,
  data: Partial<{ name: string; grade_level: SchoolGradeLevel; start_date: string; end_date: string }>
): Promise<MenuPlan> {
  return fetchJSON(`${BASE}/menus/${planId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function deleteMenuPlan(planId: number): Promise<void> {
  return fetchJSON(`${BASE}/menus/${planId}`, { method: 'DELETE' });
}

// --- Daily Menus ---

export function fetchDailyMenu(planId: number, date: string): Promise<DailyMenu> {
  return fetchJSON(`${BASE}/menus/daily?plan_id=${planId}&date=${date}`);
}

export function updateDailyMenu(planId: number, date: string, menu: DailyMenuData): Promise<DailyMenu> {
  return fetchJSON(`${BASE}/menus/daily`, {
    method: 'PUT',
    body: JSON.stringify({ plan_id: planId, date, menu }),
  });
}

export function fetchMenusRange(planId: number, start: string, end: string): Promise<DailyMenu[]> {
  return fetchJSON(`${BASE}/menus/range?plan_id=${planId}&start=${start}&end=${end}`);
}

export function copyMenuPlan(sourcePlanId: number, newName: string, startDate: string): Promise<MenuPlan> {
  return fetchJSON(`${BASE}/menus/copy`, {
    method: 'POST',
    body: JSON.stringify({ source_plan_id: sourcePlanId, new_name: newName, start_date: startDate }),
  });
}

// --- Nutrition Analysis ---

export function analyzeDailyNutrition(
  menu: DailyMenuData,
  gradeLevel: SchoolGradeLevel
): Promise<DailyNutritionResult> {
  return fetchJSON(`${BASE}/menu/nutrition/daily`, {
    method: 'POST',
    body: JSON.stringify({ menu, grade_level: gradeLevel }),
  });
}

export function analyzeWeeklyNutrition(
  planId: number,
  startDate: string
): Promise<WeeklyNutritionResult> {
  return fetchJSON(`${BASE}/menu/nutrition/weekly`, {
    method: 'POST',
    body: JSON.stringify({ plan_id: planId, start_date: startDate }),
  });
}

export function fetchNutritionStandards(gradeLevel: SchoolGradeLevel) {
  return fetchJSON<{
    grade_level: string;
    label: string;
    age: number;
    nutrients: { key: string; name: string; unit: string; value: number }[];
  }>(`${BASE}/menu/nutrition/standards/${gradeLevel}`);
}

// --- Food & Recipe ---

export function fetchFoods(): Promise<FoodItem[]> {
  return fetchJSON(`${BASE}/foods`);
}

export function fetchRecipes(): Promise<Recipe[]> {
  return fetchJSON(`${BASE}/recipes`);
}

// --- F1: 季節の食べもの ---

export function fetchSeasonalFoods(month: number): Promise<SeasonalFood[]> {
  return fetchJSON(`${BASE}/seasonal/foods?month=${month}`);
}

export function checkSeasonal(menu: DailyMenuData, month: number): Promise<SeasonalRecommendation> {
  return fetchJSON(`${BASE}/seasonal/check`, {
    method: 'POST',
    body: JSON.stringify({ menu, month }),
  });
}

// --- F2: アレルギー管理 ---

export function fetchAllergens(): Promise<AllergenInfo[]> {
  return fetchJSON(`${BASE}/allergens`);
}

export function checkAllergens(menu: DailyMenuData, excludedAllergens: string[]): Promise<AllergenWarning[]> {
  return fetchJSON(`${BASE}/allergens/check`, {
    method: 'POST',
    body: JSON.stringify({ menu, excluded_allergens: excludedAllergens }),
  });
}

// --- F4/F5: 価格予測・バッファー ---

export function estimateMenuCost(menu: DailyMenuData, targetMonth: number, bufferPct: number = 10): Promise<MenuCostEstimate> {
  return fetchJSON(`${BASE}/price/menu-cost`, {
    method: 'POST',
    body: JSON.stringify({ menu, target_month: targetMonth, buffer_pct: bufferPct }),
  });
}

// --- F6: サブプラン ---

export function fetchSubPlans(planId: number): Promise<SubPlan[]> {
  return fetchJSON(`${BASE}/menus/${planId}/sub-plans`);
}

export function createSubPlan(planId: number, data: { name: string; description?: string; excluded_allergens?: string[] }): Promise<SubPlan> {
  return fetchJSON(`${BASE}/menus/${planId}/sub-plans`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function deleteSubPlan(subPlanId: number): Promise<void> {
  return fetchJSON(`${BASE}/menus/sub-plans/${subPlanId}`, { method: 'DELETE' });
}

export function fetchSubPlanDaily(subPlanId: number, date: string) {
  return fetchJSON<{ sub_plan_id: number; date: string; menu: DailyMenuData; overrides: Record<string, unknown> }>(
    `${BASE}/menus/sub-plans/${subPlanId}/daily?date=${date}`
  );
}

export function setSubPlanOverride(subPlanId: number, date: string, slot: string, item: Record<string, unknown>) {
  return fetchJSON(`${BASE}/menus/sub-plans/${subPlanId}/override`, {
    method: 'PUT',
    body: JSON.stringify({ date, slot, item }),
  });
}

// --- F7: 食べ合わせ ---

export function checkCombinations(menu: DailyMenuData): Promise<CombinationResult> {
  return fetchJSON(`${BASE}/combinations/check`, {
    method: 'POST',
    body: JSON.stringify({ menu }),
  });
}

// --- F8: 調理工数 ---

export function estimateCookingEffort(menu: DailyMenuData): Promise<CookingEffortResult> {
  return fetchJSON(`${BASE}/cooking/effort`, {
    method: 'POST',
    body: JSON.stringify({ menu }),
  });
}
