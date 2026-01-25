import { useState, useEffect } from 'react';

// 分析タブの型定義
type AnalysisTab = 'problem' | 'cost' | 'history' | 'optimize' | 'efficiency' | 'calculator';

interface FoodItem {
  food_name: string;
  price_per_100g: number;
  energy_kcal: number;
  protein_g: number;
}

interface OptimizeResultFood {
  food_name: string;
  amount_g: number;
  cost: number;
}

interface NutrientContribution {
  food_name: string;
  amount: number;
  contribution: number;
  percentage: number;
}

interface OptimizeResultNutrient {
  name: string;
  actual: number;
  required: number;
  unit: string;
  ratio: number;
  achieved: boolean;
  contributions: NutrientContribution[];
}

interface CalcOptimizeResult {
  success: boolean;
  message: string;
  total_cost: number;
  food_amounts: OptimizeResultFood[];
  nutrients: OptimizeResultNutrient[];
}

// 最適化戦略
type OptimizeStrategy = 'strict' | 'calorie_focused' | 'balanced' | 'custom_score' | 'best_effort' | 'cost_limited';

// 食材の量制約
interface FoodConstraint {
  type: 'fixed' | 'min' | 'max' | 'range' | 'unit';
  fixed?: number;
  min?: number;
  max?: number;
  unitCount?: number;  // 個数
  unitWeight?: number; // 1個あたりのグラム数
}

// 一般的な食品の単位重量（グラム）と表示用
const COMMON_UNIT_WEIGHTS: Record<string, { name: string; weight: number }[]> = {
  '牛乳': [{ name: '学校給食パック', weight: 200 }, { name: '1パック(1L)', weight: 1000 }],
  'たまご': [{ name: '1個(M)', weight: 50 }, { name: '1個(L)', weight: 60 }],
  'とうふ': [{ name: '1丁', weight: 300 }, { name: '半丁', weight: 150 }],
  '納豆': [{ name: '1パック', weight: 45 }],
  'ヨーグルト': [{ name: '1カップ', weight: 100 }],
  'パン': [{ name: '食パン1枚', weight: 60 }, { name: 'ロールパン1個', weight: 30 }],
  'ごはん': [{ name: 'お茶碗1杯', weight: 150 }, { name: '給食1人前', weight: 200 }],
  'バナナ': [{ name: '1本', weight: 100 }],
  'りんご': [{ name: '1個', weight: 250 }],
  'みかん': [{ name: '1個', weight: 80 }],
};

// 食品の代表的な単位（表示用）
const FOOD_DISPLAY_UNITS: Record<string, { unit: string; weight: number }> = {
  '豆腐（木綿）': { unit: '1丁', weight: 400 },
  '豆腐（絹ごし）': { unit: '1丁', weight: 400 },
  '納豆': { unit: '3パック', weight: 150 },
  '鶏卵（Ｌ）': { unit: '10個', weight: 600 },
  '牛乳': { unit: '1L', weight: 1000 },
  '食パン': { unit: '6枚切', weight: 400 },
  'ロールパン': { unit: '6個', weight: 300 },
  'バナナ': { unit: '1房', weight: 1000 },
  'りんご': { unit: '1個', weight: 300 },
  'みかん': { unit: '1kg', weight: 1000 },
  'キャベツ': { unit: '1玉', weight: 1200 },
  'はくさい': { unit: '1玉', weight: 2000 },
  'だいこん': { unit: '1本', weight: 1000 },
  'たまねぎ': { unit: '1個', weight: 200 },
  'にんじん': { unit: '1本', weight: 150 },
  'じゃがいも': { unit: '1個', weight: 150 },
  'さつまいも': { unit: '1本', weight: 300 },
  'さといも': { unit: '1袋', weight: 500 },
  'ながいも': { unit: '1本', weight: 1000 },
  'ごぼう': { unit: '1本', weight: 300 },
  'れんこん': { unit: '1節', weight: 300 },
  'ほうれんそう': { unit: '1束', weight: 200 },
  'こまつな': { unit: '1束', weight: 200 },
  'ブロッコリー': { unit: '1株', weight: 300 },
  'トマト': { unit: '1個', weight: 200 },
  'ミニトマト': { unit: '1パック', weight: 200 },
  'きゅうり': { unit: '1本', weight: 100 },
  'なす': { unit: '1本', weight: 80 },
  'ピーマン': { unit: '1個', weight: 35 },
  'かぼちゃ': { unit: '1/4個', weight: 400 },
  'もやし': { unit: '1袋', weight: 200 },
  'えのきたけ': { unit: '1袋', weight: 200 },
  'しめじ': { unit: '1パック', weight: 100 },
  'まいたけ': { unit: '1パック', weight: 100 },
  'しいたけ（生）': { unit: '1パック', weight: 100 },
  'エリンギ': { unit: '1パック', weight: 100 },
  '厚揚げ': { unit: '1枚', weight: 300 },
  '油揚げ': { unit: '3枚', weight: 150 },
  'ヨーグルト（プレーン）': { unit: '1カップ', weight: 400 },
  'チーズ（プロセス）': { unit: '6個', weight: 150 },
  '鶏肉（むね）': { unit: '1枚', weight: 250 },
  '鶏肉（もも）': { unit: '1枚', weight: 250 },
  '豚肉（もも）': { unit: '100g', weight: 100 },
  '豚肉（ロース）': { unit: '100g', weight: 100 },
  '牛肉（もも）': { unit: '100g', weight: 100 },
  'さけ': { unit: '1切', weight: 80 },
  'さば': { unit: '1切', weight: 80 },
  'あじ': { unit: '1尾', weight: 150 },
  'いわし': { unit: '1尾', weight: 80 },
  'ちくわ': { unit: '1本', weight: 30 },
  'サラダ油': { unit: '1L', weight: 900 },
  'ごま油': { unit: '200ml', weight: 180 },
  'オリーブオイル': { unit: '500ml', weight: 450 },
  '米（精白米）': { unit: '5kg', weight: 5000 },
  'うどん（乾）': { unit: '1kg', weight: 1000 },
  'そば（乾）': { unit: '1kg', weight: 1000 },
  'スパゲッティ（乾）': { unit: '500g', weight: 500 },
  '即席めん': { unit: '5食', weight: 500 },
};

// プリセット定義
const FOOD_PRESETS: Record<string, { name: string; description: string; foods: string[]; fixedAmounts?: Record<string, number> }> = {
  school_basic: {
    name: '給食基本セット',
    description: '白米0.5合＋牛乳パック＋おかず',
    foods: ['米（精白米）', '牛乳', '鶏卵（Ｌ）', '豆腐（木綿）', 'キャベツ', 'にんじん', 'たまねぎ'],
    fixedAmounts: { '米（精白米）': 75, '牛乳': 200 },  // 0.5合≒75g（炊飯後150g相当）
  },
  school_lunch: {
    name: '給食定番',
    description: '学校給食でよく使われる食材',
    foods: ['米（精白米）', '食パン', '牛乳', '鶏卵（Ｌ）', '豆腐（木綿）', '鶏肉（むね）', '豚肉（もも）', 'さけ', 'あじ', 'キャベツ', 'にんじん', 'たまねぎ', 'じゃがいも', 'ほうれんそう', 'こまつな', 'だいこん', 'はくさい', 'きゅうり', 'トマト', 'ブロッコリー', '牛乳', '納豆'],
  },
  school_bread: {
    name: '給食パンセット',
    description: 'パン＋牛乳＋おかず',
    foods: ['食パン', 'ロールパン', '牛乳', '鶏卵（Ｌ）', 'ハム（ロース）', 'キャベツ', 'きゅうり', 'トマト', 'レタス'],
    fixedAmounts: { '食パン': 60, '牛乳': 200 },
  },
  protein: {
    name: 'たんぱく源',
    description: '肉・魚・卵・豆類中心',
    foods: ['鶏卵（Ｌ）', '豆腐（木綿）', '豆腐（絹ごし）', '納豆', '厚揚げ', '鶏肉（むね）', '鶏肉（もも）', '鶏肉（ささみ）', '豚肉（もも）', '豚肉（ロース）', '牛肉（もも）', 'さけ', 'さば', 'あじ', 'いわし', 'まぐろ（赤身）', 'えび', 'あさり', '牛乳', 'ヨーグルト（プレーン）', 'チーズ（プロセス）', '豆乳'],
  },
  vegetables: {
    name: '野菜中心',
    description: '野菜・きのこ・海藻',
    foods: ['キャベツ', 'にんじん', 'たまねぎ', 'じゃがいも', 'ほうれんそう', 'こまつな', 'だいこん', 'はくさい', 'きゅうり', 'トマト', 'ミニトマト', 'ブロッコリー', 'ピーマン', 'なす', 'かぼちゃ', 'えのきたけ', 'しめじ', 'しいたけ（生）', 'まいたけ', 'エリンギ', 'わかめ（乾燥）', 'ひじき（乾燥）'],
  },
  budget: {
    name: '節約食材',
    description: 'コスパの良い食材',
    foods: ['米（精白米）', 'うどん（乾）', '食パン', '鶏卵（Ｌ）', '豆腐（木綿）', '納豆', 'はくさい', 'キャベツ', 'たまねぎ', 'にんじん', 'だいこん', 'じゃがいも', 'バナナ', '牛乳', '鶏肉（むね）', 'いわし', 'ちくわ', 'えのきたけ'],
  },
  fish: {
    name: '魚介中心',
    description: '魚・貝・えび',
    foods: ['さけ', 'さば', 'あじ', 'いわし', 'さんま', 'ぶり', 'たら', 'ほっけ', 'かつお', 'まぐろ（赤身）', 'えび', 'あさり', 'しじみ', 'かまぼこ', 'ちくわ'],
  },
};

interface NutrientData {
  key: string;
  name: string;
  lunch: number;
  daily: number;
  ratio: number;
  unit: string;
}

interface AgeData {
  age: number;
  nutrients: NutrientData[];
}

interface CostOptResult {
  success: boolean;
  min_cost: number;
  total_weight_g: number;
  foods: Array<{ name: string; amount_g: number; cost: number }>;
  nutrients: Array<{ key: string; name: string; target: number; actual: number; ratio: number; achieved: boolean }>;
}

interface PriceHistory {
  price_summary: {
    five_years_ago: { change_percent: number };
    ten_years_ago: { change_percent: number };
    fifteen_years_ago?: { change_percent: number };
    category_changes: Record<string, number>;
  };
  lunch_costs: {
    elementary: Array<{ year: number; monthly_fee: number; material_cost_per_meal: number }>;
    junior_high: Array<{ year: number; monthly_fee: number; material_cost_per_meal: number }>;
  };
}

interface HistoricalOpt {
  years: Array<{ year: number; min_cost: number; change_from_2010?: number }>;
  base_year?: number;
}

interface YearsComparison {
  years: Array<{ year: number; index: number; change_from_2010: number; change_from_prev: number }>;
  base_year: number;
}

interface SeasonalData {
  categories: Record<string, {
    yearly_index: number;
    quarters: Record<string, { factor: number; index: number; label: string }>;
  }>;
  food_examples: Record<string, Record<string, number>>;
  food_examples_by_year: Record<number, Record<string, Record<string, number>>>;
  available_years: number[];
  quarters: Record<string, string>;
}

interface CategoryTrends {
  categories: Record<string, Array<{ year: number; index: number; change_from_2010: number }>>;
  years: number[];
}

interface NutrientCostFood {
  name: string;
  cost_per_display_unit: number;
  amount_per_100g: number;
}

// レシピ関連の型定義
interface RecipeIngredient {
  original_name: string;
  amount_text: string;
  amount_g: number | null;
  matched_food: string | null;
}

interface Recipe {
  id: string;
  name: string;
  servings: number;
  source_url: string | null;
  ingredients: RecipeIngredient[];
}

interface NutrientCostInfo {
  name: string;
  unit: string;
  display_unit: string;
  cheapest_cost: number;
  top_foods: NutrientCostFood[];
}

type NutrientCostData = Record<string, NutrientCostInfo>;

// 環境変数からAPI URLを取得（本番環境ではRailwayのURL）
const API_BASE = import.meta.env.VITE_API_URL || '/api';

export default function App() {
  const [activeTab, setActiveTab] = useState<AnalysisTab>('problem');
  const [selectedAge, setSelectedAge] = useState(10);
  const [selectedSeasonalYear, setSelectedSeasonalYear] = useState(2026);
  const [ageComparison, setAgeComparison] = useState<AgeData[]>([]);
  const [costOptResult, setCostOptResult] = useState<CostOptResult | null>(null);
  const [priceHistory, setPriceHistory] = useState<PriceHistory | null>(null);
  const [historicalOpt, setHistoricalOpt] = useState<HistoricalOpt | null>(null);
  const [nutrientCostData, setNutrientCostData] = useState<NutrientCostData | null>(null);
  const [yearsComparison, setYearsComparison] = useState<YearsComparison | null>(null);
  const [seasonalData, setSeasonalData] = useState<SeasonalData | null>(null);
  // categoryTrends は将来のカテゴリ別トレンドチャート用に保持
  const [, setCategoryTrends] = useState<CategoryTrends | null>(null);
  const [loading, setLoading] = useState(true);

  // 計算ツール用のstate
  const [allFoods, setAllFoods] = useState<FoodItem[]>([]);
  const [selectedFoods, setSelectedFoods] = useState<Set<string>>(new Set());
  const [calcAge, setCalcAge] = useState(10);
  const [calcGender, setCalcGender] = useState<'male' | 'female'>('male');
  const [calcResult, setCalcResult] = useState<CalcOptimizeResult | null>(null);
  const [calcLoading, setCalcLoading] = useState(false);
  const [foodSearch, setFoodSearch] = useState('');

  // 最適化オプション
  const [strategy, setStrategy] = useState<OptimizeStrategy>('balanced');
  const [maxFoodAmount, setMaxFoodAmount] = useState(1500);
  const [foodConstraints, setFoodConstraints] = useState<Record<string, FoodConstraint>>({});
  const [maxCost, setMaxCost] = useState(500);
  const [mealType, setMealType] = useState<'daily' | 'per_meal' | 'school_lunch'>('per_meal');

  // 給食基本セット（ベース）のトグル
  const [baseSetEnabled, setBaseSetEnabled] = useState(false);

  // 結果から除外する食材（再計算用）
  const [excludedFoods, setExcludedFoods] = useState<Set<string>>(new Set());

  // 定番料理レシピ
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  // 給食基本セットの定義（固定量）
  const BASE_SET_FOODS: Record<string, number> = {
    '米（精白米）': 150,  // 1合 = 約150g（炊飯前）
    '牛乳': 200,          // 1パック = 200ml
    '納豆': 45,           // 1パック = 45g
  };

  // データ取得
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/lunch/age-comparison`).then(r => r.json()),
      fetch(`${API_BASE}/price/history`).then(r => r.json()),
      fetch(`${API_BASE}/price/historical-optimization`).then(r => r.json()),
      fetch(`${API_BASE}/nutrients/cost-per-unit`).then(r => r.json()),
      fetch(`${API_BASE}/price/years-comparison`).then(r => r.json()),
      fetch(`${API_BASE}/price/seasonal`).then(r => r.json()),
      fetch(`${API_BASE}/price/category-trends`).then(r => r.json()),
    ])
      .then(([ages, prices, histOpt, nutrientCost, years, seasonal, catTrends]) => {
        // 年齢比較データを整形
        const formatted = ages.map((a: any) => ({
          age: a.age,
          nutrients: Object.entries(a.nutrients).map(([key, val]: [string, any]) => ({
            key,
            name: val.name,
            lunch: val.lunch,
            daily: val.daily_male,
            ratio: val.ratio_male,
            unit: key.includes('kcal') ? 'kcal' : key.includes('_mg') ? 'mg' : key.includes('_ug') ? 'μg' : 'g',
          })),
        }));
        setAgeComparison(formatted);
        setPriceHistory(prices);
        setHistoricalOpt(histOpt);
        setNutrientCostData(nutrientCost);
        setYearsComparison(years);
        setSeasonalData(seasonal);
        setCategoryTrends(catTrends);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // コスト最適化を実行
  useEffect(() => {
    if (activeTab === 'optimize') {
      fetch(`${API_BASE}/lunch/optimize-cost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: selectedAge, gender: 'male' }),
      })
        .then(r => r.json())
        .then(setCostOptResult);
    }
  }, [activeTab, selectedAge]);

  // 食品リスト取得（計算ツール用）
  useEffect(() => {
    if (activeTab === 'calculator' && allFoods.length === 0) {
      fetch(`${API_BASE}/foods`)
        .then(r => r.json())
        .then(setAllFoods);
    }
  }, [activeTab, allFoods.length]);

  // レシピデータ取得
  useEffect(() => {
    if (activeTab === 'calculator' && recipes.length === 0) {
      fetch(`${API_BASE}/recipes`)
        .then(r => r.json())
        .then(setRecipes)
        .catch(console.error);
    }
  }, [activeTab, recipes.length]);

  // 選択食品で最適化計算
  const runOptimization = async (excludeList?: Set<string>) => {
    // 除外リストをリセット（新規計算時）または使用（再計算時）
    const currentExcludes = excludeList || new Set<string>();
    if (!excludeList) {
      setExcludedFoods(new Set());
    }

    // ベースセット + 選択食材を結合
    const allSelectedFoods = new Set(selectedFoods);
    if (baseSetEnabled) {
      Object.keys(BASE_SET_FOODS).forEach(f => allSelectedFoods.add(f));
    }

    // 除外された食材を削除
    currentExcludes.forEach(f => allSelectedFoods.delete(f));

    if (allSelectedFoods.size === 0) return;
    setCalcLoading(true);
    try {
      // 固定量の食材をリストに変換（fixed と unit の両方に対応）
      const fixedFoods = Object.entries(foodConstraints)
        .filter(([name, c]) => allSelectedFoods.has(name) && (c.type === 'fixed' || c.type === 'unit'))
        .map(([name, c]) => {
          if (c.type === 'unit') {
            return { food_name: name, amount_g: c.unitWeight! * c.unitCount! };
          }
          return { food_name: name, amount_g: c.fixed! };
        });

      // 最小量制約（min type）
      const minFoods = Object.entries(foodConstraints)
        .filter(([name, c]) => allSelectedFoods.has(name) && c.type === 'min' && c.min && c.min > 0)
        .map(([name, c]) => ({ food_name: name, min_g: c.min! }));

      // ベースセットの固定量を追加（foodConstraintsで上書きされていない場合、除外されていない場合）
      if (baseSetEnabled) {
        for (const [foodName, amount] of Object.entries(BASE_SET_FOODS)) {
          if (!fixedFoods.some(f => f.food_name === foodName) && !currentExcludes.has(foodName)) {
            fixedFoods.push({ food_name: foodName, amount_g: amount });
          }
        }
      }

      const res = await fetch(`${API_BASE}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_foods: Array.from(allSelectedFoods),
          age: calcAge,
          gender: calcGender,
          strategy: strategy,
          max_food_amount_g: maxFoodAmount,
          fixed_foods: fixedFoods,
          min_foods: minFoods,
          max_cost: maxCost,
          meal_type: mealType,
        }),
      });
      const data = await res.json();
      setCalcResult(data);
    } catch (e) {
      console.error(e);
    }
    setCalcLoading(false);
  };

  // 食材を除外して再計算
  const toggleExcludeFood = (foodName: string) => {
    setExcludedFoods(prev => {
      const next = new Set(prev);
      if (next.has(foodName)) {
        next.delete(foodName);
      } else {
        next.add(foodName);
      }
      return next;
    });
  };

  // 除外リストで再計算
  const recalculateWithExclusions = () => {
    runOptimization(excludedFoods);
  };

  // プリセット適用（追加モード対応）
  const applyPreset = (presetKey: string, additive: boolean = false) => {
    if (presetKey === 'all') {
      setSelectedFoods(new Set(allFoods.map(f => f.food_name)));
      if (!additive) setFoodConstraints({});
    } else if (presetKey === 'clear') {
      setSelectedFoods(new Set());
      setFoodConstraints({});
      setBaseSetEnabled(false);
    } else {
      const preset = FOOD_PRESETS[presetKey];
      if (preset) {
        const matchingFoods = allFoods
          .filter(f => preset.foods.some(p => f.food_name === p || f.food_name.includes(p)))
          .map(f => f.food_name);

        if (additive) {
          // 追加モード：既存の選択に追加
          setSelectedFoods(prev => {
            const next = new Set(prev);
            matchingFoods.forEach(f => next.add(f));
            return next;
          });
          // 固定量も追加（既存を上書きしない）
          if (preset.fixedAmounts) {
            setFoodConstraints(prev => {
              const next = { ...prev };
              for (const [foodName, amount] of Object.entries(preset.fixedAmounts!)) {
                const actualFood = allFoods.find(f => f.food_name === foodName || f.food_name.includes(foodName));
                if (actualFood && !next[actualFood.food_name]) {
                  next[actualFood.food_name] = { type: 'fixed', fixed: amount };
                }
              }
              return next;
            });
          }
        } else {
          // 置換モード
          setSelectedFoods(new Set(matchingFoods));
          if (preset.fixedAmounts) {
            const newConstraints: Record<string, FoodConstraint> = {};
            for (const [foodName, amount] of Object.entries(preset.fixedAmounts)) {
              const actualFood = allFoods.find(f => f.food_name === foodName || f.food_name.includes(foodName));
              if (actualFood) {
                newConstraints[actualFood.food_name] = { type: 'fixed', fixed: amount };
              }
            }
            setFoodConstraints(newConstraints);
          } else {
            setFoodConstraints({});
          }
        }
      }
    }
  };

  // 食材の制約を更新
  const updateFoodConstraint = (foodName: string, constraint: FoodConstraint | null) => {
    setFoodConstraints(prev => {
      const next = { ...prev };
      if (constraint === null) {
        delete next[foodName];
      } else {
        next[foodName] = constraint;
      }
      return next;
    });
  };

  const toggleFood = (name: string) => {
    setSelectedFoods(prev => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  // レシピを食材テンプレートとして適用（追加モード・1人前の最小量を設定）
  const applyRecipe = (recipe: Recipe) => {
    // レシピの食材をマッチングして選択に追加
    const matchedFoods: { foodName: string; amountPerServing: number }[] = [];
    recipe.ingredients.forEach(ing => {
      if (ing.matched_food && ing.amount_g) {
        // マッチした食品名を使用
        const food = allFoods.find(f => f.food_name === ing.matched_food);
        if (food) {
          // 1人前の量を計算
          const amountPerServing = Math.round(ing.amount_g / recipe.servings);
          matchedFoods.push({
            foodName: food.food_name,
            amountPerServing,
          });
        }
      }
    });

    // 選択に追加
    setSelectedFoods(prev => {
      const next = new Set(prev);
      matchedFoods.forEach(f => next.add(f.foodName));
      return next;
    });

    // 1人前の量を最小量として設定（既存の制約がある場合は加算）
    setFoodConstraints(prev => {
      const next = { ...prev };
      matchedFoods.forEach(({ foodName, amountPerServing }) => {
        if (amountPerServing <= 0) return;

        const existing = next[foodName];
        if (existing) {
          // 既存の制約から現在の量を取得して加算
          let currentAmount = 0;
          if (existing.type === 'fixed' && existing.fixed) {
            currentAmount = existing.fixed;
          } else if (existing.type === 'min' && existing.min) {
            currentAmount = existing.min;
          } else if (existing.type === 'unit' && existing.unitWeight && existing.unitCount) {
            currentAmount = existing.unitWeight * existing.unitCount;
          }
          // 加算して最小量として設定
          next[foodName] = { type: 'min', min: currentAmount + amountPerServing };
        } else {
          // 新規は最小量として設定
          next[foodName] = { type: 'min', min: amountPerServing };
        }
      });
      return next;
    });
  };

  const filteredFoods = allFoods.filter(f =>
    f.food_name.toLowerCase().includes(foodSearch.toLowerCase())
  );

  if (loading) {
    return (
      <div className="app-container">
        <header className="app-header">
          <h1>学校給食の栄養分析</h1>
        </header>
        <main className="loading-state">読み込み中...</main>
      </div>
    );
  }

  const currentAgeData = ageComparison.find(a => a.age === selectedAge);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>学校給食の栄養分析</h1>
        <p className="subtitle">現状の問題点と最適化の可能性</p>
      </header>

      {/* タブナビゲーション */}
      <nav className="tab-nav">
        <button
          className={activeTab === 'problem' ? 'active' : ''}
          onClick={() => setActiveTab('problem')}
        >
          問題提起
        </button>
        <button
          className={activeTab === 'cost' ? 'active' : ''}
          onClick={() => setActiveTab('cost')}
        >
          コスト分析
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          価格推移
        </button>
        <button
          className={activeTab === 'optimize' ? 'active' : ''}
          onClick={() => setActiveTab('optimize')}
        >
          最適化提案
        </button>
        <button
          className={activeTab === 'efficiency' ? 'active' : ''}
          onClick={() => setActiveTab('efficiency')}
        >
          栄養素コスパ
        </button>
        <button
          className={activeTab === 'calculator' ? 'active' : ''}
          onClick={() => setActiveTab('calculator')}
        >
          計算ツール
        </button>
      </nav>

      <main className="main-content">
        {/* 問題提起タブ */}
        {activeTab === 'problem' && (
          <section className="analysis-section">
            <div className="section-header">
              <h2>給食は1日の栄養の1/3を担えているか？</h2>
              <div className="age-selector">
                {[7, 10, 13].map(age => (
                  <button
                    key={age}
                    className={selectedAge === age ? 'active' : ''}
                    onClick={() => setSelectedAge(age)}
                  >
                    {age}歳
                  </button>
                ))}
              </div>
            </div>

            <div className="key-finding">
              <div className="finding-icon">!</div>
              <div className="finding-text">
                <strong>発見:</strong> 給食基準は1日必要量の<strong>30-35%</strong>しかカバーしていません。
                1日3食なら各食<strong>33.3%</strong>が期待されますが、多くの栄養素で不足しています。
              </div>
            </div>

            <div className="nutrient-grid">
              {currentAgeData?.nutrients.map(n => {
                const gap = n.ratio - 33.3;
                const isDeficit = gap < 0;
                const isSevere = gap < -5;

                return (
                  <div key={n.key} className={`nutrient-card ${isSevere ? 'severe' : isDeficit ? 'warning' : 'ok'}`}>
                    <div className="nutrient-name">{n.name}</div>
                    <div className="nutrient-values">
                      <span className="lunch-value">{n.lunch}{n.unit}</span>
                      <span className="separator">/</span>
                      <span className="daily-value">{n.daily}{n.unit}</span>
                    </div>
                    <div className="ratio-bar-container">
                      <div className="ratio-bar" style={{ width: `${Math.min(n.ratio, 100)}%` }} />
                      <div className="expected-line" />
                    </div>
                    <div className="ratio-label">
                      {n.ratio.toFixed(1)}%
                      <span className={`gap ${isDeficit ? 'negative' : 'positive'}`}>
                        ({gap >= 0 ? '+' : ''}{gap.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="problem-explanation">
              <h3>なぜこれが問題なのか？</h3>
              <ul>
                <li><strong>朝食欠食</strong>: 子どもの約15%が朝食を食べていない（令和4年度調査）</li>
                <li><strong>夕食の偏り</strong>: 共働き世帯の増加で夕食の栄養バランスが崩れやすい</li>
                <li><strong>給食への依存</strong>: 低所得世帯では給食が1日の主要な栄養源</li>
              </ul>
            </div>
          </section>
        )}

        {/* コスト分析タブ */}
        {activeTab === 'cost' && priceHistory && (
          <section className="analysis-section">
            <div className="section-header">
              <h2>給食の食材費はいくらか？</h2>
            </div>

            <div className="cost-comparison">
              <div className="cost-card elementary">
                <h3>小学校</h3>
                <div className="cost-timeline">
                  {priceHistory.lunch_costs.elementary.map((d, i) => (
                    <div key={d.year} className="cost-year">
                      <span className="year">{d.year}年</span>
                      <span className="monthly">月額 ¥{d.monthly_fee.toLocaleString()}</span>
                      <span className="per-meal">1食材料費 ¥{d.material_cost_per_meal}</span>
                      {i > 0 && (
                        <span className="change">
                          +{Math.round((d.monthly_fee / priceHistory.lunch_costs.elementary[0].monthly_fee - 1) * 100)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="cost-card junior-high">
                <h3>中学校</h3>
                <div className="cost-timeline">
                  {priceHistory.lunch_costs.junior_high.map((d, i) => (
                    <div key={d.year} className="cost-year">
                      <span className="year">{d.year}年</span>
                      <span className="monthly">月額 ¥{d.monthly_fee.toLocaleString()}</span>
                      <span className="per-meal">1食材料費 ¥{d.material_cost_per_meal}</span>
                      {i > 0 && (
                        <span className="change">
                          +{Math.round((d.monthly_fee / priceHistory.lunch_costs.junior_high[0].monthly_fee - 1) * 100)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="cost-insight">
              <h3>1食あたり¥200-260で何ができるか？</h3>
              <p>
                この予算で1日の<strong>1/3の栄養</strong>を確実に満たすことは可能でしょうか？
                「最適化提案」タブで検証します。
              </p>
            </div>
          </section>
        )}

        {/* 価格推移タブ */}
        {activeTab === 'history' && priceHistory && historicalOpt && (
          <section className="analysis-section">
            <div className="section-header">
              <h2>食料品価格は15年でどう変わったか？</h2>
            </div>

            <div className="price-summary">
              <div className="price-change-card">
                <span className="period">5年前比</span>
                <span className="change-value">+{priceHistory.price_summary.five_years_ago.change_percent}%</span>
              </div>
              <div className="price-change-card">
                <span className="period">10年前比</span>
                <span className="change-value">+{priceHistory.price_summary.ten_years_ago.change_percent}%</span>
              </div>
              {priceHistory.price_summary.fifteen_years_ago && (
                <div className="price-change-card highlight">
                  <span className="period">15年前比</span>
                  <span className="change-value">+{priceHistory.price_summary.fifteen_years_ago.change_percent}%</span>
                </div>
              )}
            </div>

            {/* 年次価格推移チャート */}
            {yearsComparison && (
              <div className="yearly-chart">
                <h3>物価指数の推移（2010年〜2026年）</h3>
                <div className="chart-container">
                  {yearsComparison.years.map((y) => {
                    const maxChange = Math.max(...yearsComparison.years.map(yr => yr.change_from_2010));
                    const heightPercent = maxChange > 0 ? (y.change_from_2010 / maxChange) * 100 : 0;
                    return (
                      <div key={y.year} className="chart-bar-wrapper">
                        <div className="chart-bar" style={{ height: `${Math.max(heightPercent, 5)}%` }}>
                          <span className="bar-value">+{y.change_from_2010}%</span>
                        </div>
                        <span className={`bar-year ${y.year === 2026 ? 'current' : ''}`}>{y.year}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 季節変動 */}
            {seasonalData && (
              <div className="seasonal-section">
                <h3>季節別価格変動（4月/7月/10月/1月 15日基準）</h3>
                <p className="seasonal-desc">野菜を中心に、季節により10-20%の価格変動があります。</p>
                <div className="seasonal-grid">
                  {Object.entries(seasonalData.categories).slice(0, 4).map(([cat, data]) => (
                    <div key={cat} className="seasonal-card">
                      <h4>{cat}</h4>
                      <div className="quarter-bars">
                        {Object.entries(data.quarters).map(([q, qData]) => (
                          <div key={q} className="quarter-item">
                            <div
                              className={`quarter-bar ${qData.factor > 1.05 ? 'high' : qData.factor < 0.95 ? 'low' : ''}`}
                              style={{ height: `${qData.factor * 50}px` }}
                            >
                              <span className="factor">{qData.factor.toFixed(2)}</span>
                            </div>
                            <span className="quarter-label">{qData.label.replace('日', '')}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* 食材別季節価格例 */}
                <div className="food-seasonal-examples">
                  <div className="seasonal-header">
                    <h4>代表的な野菜の季節価格（100gあたり・円）</h4>
                    <div className="year-tabs">
                      {seasonalData.available_years?.map(year => (
                        <button
                          key={year}
                          className={selectedSeasonalYear === year ? 'active' : ''}
                          onClick={() => setSelectedSeasonalYear(year)}
                        >
                          {year}年
                        </button>
                      ))}
                    </div>
                  </div>
                  <table className="seasonal-table">
                    <thead>
                      <tr>
                        <th>食材</th>
                        <th>4月15日</th>
                        <th>7月15日</th>
                        <th>10月15日</th>
                        <th>1月15日</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(
                        seasonalData.food_examples_by_year?.[selectedSeasonalYear] || seasonalData.food_examples
                      ).map(([food, prices]) => (
                        <tr key={food}>
                          <td>{food}</td>
                          <td className={prices.Q1_Apr === Math.min(...Object.values(prices)) ? 'low-price' : prices.Q1_Apr === Math.max(...Object.values(prices)) ? 'high-price' : ''}>
                            ¥{prices.Q1_Apr}
                          </td>
                          <td className={prices.Q2_Jul === Math.min(...Object.values(prices)) ? 'low-price' : prices.Q2_Jul === Math.max(...Object.values(prices)) ? 'high-price' : ''}>
                            ¥{prices.Q2_Jul}
                          </td>
                          <td className={prices.Q3_Oct === Math.min(...Object.values(prices)) ? 'low-price' : prices.Q3_Oct === Math.max(...Object.values(prices)) ? 'high-price' : ''}>
                            ¥{prices.Q3_Oct}
                          </td>
                          <td className={prices.Q4_Jan === Math.min(...Object.values(prices)) ? 'low-price' : prices.Q4_Jan === Math.max(...Object.values(prices)) ? 'high-price' : ''}>
                            ¥{prices.Q4_Jan}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="category-changes">
              <h3>カテゴリ別上昇率（2015年比）</h3>
              <div className="category-grid">
                {Object.entries(priceHistory.price_summary.category_changes).map(([cat, ratio]) => (
                  <div key={cat} className="category-item">
                    <span className="category-name">{cat}</span>
                    <span className="category-change">+{Math.round((ratio - 1) * 100)}%</span>
                    <div className="category-bar" style={{ width: `${(ratio - 1) * 200}%` }} />
                  </div>
                ))}
              </div>
            </div>

            <div className="historical-optimization">
              <h3>最適化コストの推移（10歳男子・1食分）</h3>
              <div className="opt-timeline">
                {historicalOpt.years.map((y, i) => (
                  <div key={y.year} className={`opt-year ${i === historicalOpt.years.length - 1 ? 'current' : ''}`}>
                    <span className="year">{y.year}年</span>
                    <span className="cost">¥{y.min_cost}</span>
                    {i > 0 && y.change_from_2010 !== undefined && (
                      <span className="change">+{y.change_from_2010}%</span>
                    )}
                  </div>
                ))}
              </div>
              <p className="insight">
                同じ栄養を取るのに、2010年より<strong>約{historicalOpt.years[historicalOpt.years.length - 1]?.change_from_2010 || 0}%</strong>多くコストがかかります。
              </p>
            </div>
          </section>
        )}

        {/* 最適化提案タブ */}
        {activeTab === 'optimize' && (
          <section className="analysis-section">
            <div className="section-header">
              <h2>1食で1/3の栄養を最安で取るには？</h2>
              <div className="age-selector">
                {[7, 10, 13].map(age => (
                  <button
                    key={age}
                    className={selectedAge === age ? 'active' : ''}
                    onClick={() => setSelectedAge(age)}
                  >
                    {age}歳
                  </button>
                ))}
              </div>
            </div>

            {costOptResult?.success ? (
              <>
                <div className="optimization-result">
                  <div className="result-highlight">
                    <span className="label">最小コスト</span>
                    <span className="value">¥{costOptResult.min_cost}</span>
                    <span className="note">全栄養素の1/3を達成</span>
                  </div>
                  <div className="result-weight">
                    <span>総重量: {costOptResult.total_weight_g}g</span>
                  </div>
                </div>

                <div className="optimal-foods">
                  <h3>最適な食材の組み合わせ</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>食材</th>
                        <th>量</th>
                        <th>価格</th>
                      </tr>
                    </thead>
                    <tbody>
                      {costOptResult.foods.slice(0, 8).map(f => (
                        <tr key={f.name}>
                          <td>{f.name}</td>
                          <td>{f.amount_g}g</td>
                          <td>¥{f.cost}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="nutrient-achievement">
                  <h3>栄養素達成状況</h3>
                  <div className="achievement-grid">
                    {costOptResult.nutrients.map(n => (
                      <div key={n.key} className={`achievement-item ${n.achieved ? 'achieved' : ''}`}>
                        <span className="name">{n.name}</span>
                        <span className="ratio">{n.ratio}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="conclusion">
                  <h3>結論</h3>
                  <p>
                    <strong>¥{costOptResult.min_cost}</strong>で1日の1/3の栄養を達成できます。
                    現在の給食食材費（約¥200-260）とほぼ同等であり、
                    <strong>適切な食材選択により、現行予算でも栄養改善は可能</strong>です。
                  </p>
                  <p>
                    問題は<strong>栄養基準自体が低く設定されている</strong>ことにあります。
                  </p>
                </div>
              </>
            ) : (
              <div className="loading-state">最適化計算中...</div>
            )}
          </section>
        )}

        {/* 栄養素コスパタブ */}
        {activeTab === 'efficiency' && nutrientCostData && (
          <section className="analysis-section">
            <div className="section-header">
              <h2>各栄養素を最も安く摂取できる食材は？</h2>
            </div>

            <div className="efficiency-intro">
              <p>
                栄養素ごとに「1単位あたりの価格」を計算し、コスパの良い食材を特定しました。
                給食の予算制約下で栄養価を高めるためのヒントになります。
              </p>
            </div>

            <div className="nutrient-cost-grid">
              {Object.entries(nutrientCostData).map(([key, info]) => (
                <div key={key} className="nutrient-cost-card">
                  <div className="nutrient-cost-header">
                    <span className="nutrient-cost-name">{info.name}</span>
                    <span className="nutrient-cost-unit">/{info.display_unit}</span>
                  </div>
                  <div className="cheapest-cost">
                    最安: <strong>¥{info.cheapest_cost.toFixed(1)}</strong>
                  </div>
                  <div className="top-foods-list">
                    {info.top_foods.map((food, i) => (
                      <div key={food.name} className={`top-food-item ${i === 0 ? 'best' : ''}`}>
                        <span className="rank">{i + 1}</span>
                        <span className="food-name">{food.name}</span>
                        <span className="food-cost">¥{food.cost_per_display_unit.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="efficiency-insight">
              <h3>分析からわかること</h3>
              <ul>
                <li>
                  <strong>たんぱく質</strong>: 鶏卵・豆腐などが圧倒的にコスパが良い
                </li>
                <li>
                  <strong>ビタミン類</strong>: 野菜の種類により大きな価格差がある
                </li>
                <li>
                  <strong>ミネラル</strong>: 特定の食材に集中しており、選択が重要
                </li>
              </ul>
              <p className="insight-note">
                ※ 価格は東京都中央卸売市場の相場に基づいています
              </p>
            </div>
          </section>
        )}

        {/* 計算ツールタブ */}
        {activeTab === 'calculator' && (
          <section className="analysis-section calculator-section">
            <div className="section-header">
              <h2>食材選択で最適化計算</h2>
            </div>

            {/* 基本設定 */}
            <div className="calc-settings">
              <div className="calc-setting-group">
                <label>年齢:</label>
                <select value={calcAge} onChange={e => setCalcAge(Number(e.target.value))}>
                  {[6, 7, 8, 9, 10, 11, 12, 13, 14, 15].map(age => (
                    <option key={age} value={age}>{age}歳</option>
                  ))}
                </select>
              </div>
              <div className="calc-setting-group">
                <label>性別:</label>
                <select value={calcGender} onChange={e => setCalcGender(e.target.value as 'male' | 'female')}>
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                </select>
              </div>
              <div className="calc-setting-group">
                <label>基準:</label>
                <select value={mealType} onChange={e => setMealType(e.target.value as 'daily' | 'per_meal' | 'school_lunch')}>
                  <option value="per_meal">1食分（1日の1/3）</option>
                  <option value="daily">1日分</option>
                  <option value="school_lunch">給食基準</option>
                </select>
              </div>
            </div>

            <div className="calc-settings">
              <div className="calc-setting-group">
                <label>最適化戦略:</label>
                <select value={strategy} onChange={e => setStrategy(e.target.value as OptimizeStrategy)}>
                  <option value="balanced">バランス型（推奨）</option>
                  <option value="best_effort">ベストエフォート（必ず結果を返す）</option>
                  <option value="cost_limited">コスト制限（予算内で最大化）</option>
                  <option value="calorie_focused">カロリー重視</option>
                  <option value="strict">厳密（全栄養素を満たす）</option>
                </select>
              </div>
              <div className="calc-setting-group">
                <label>最大量:</label>
                <select value={maxFoodAmount} onChange={e => setMaxFoodAmount(Number(e.target.value))}>
                  <option value={500}>500g（軽食）</option>
                  <option value={800}>800g（1食分）</option>
                  <option value={1500}>1500g（1日分）</option>
                  <option value={3000}>3000g（制限なし）</option>
                </select>
              </div>
              {strategy === 'cost_limited' && (
                <div className="calc-setting-group">
                  <label>予算上限:</label>
                  <select value={maxCost} onChange={e => setMaxCost(Number(e.target.value))}>
                    <option value={100}>¥100</option>
                    <option value={200}>¥200</option>
                    <option value={300}>¥300</option>
                    <option value={500}>¥500</option>
                    <option value={800}>¥800</option>
                    <option value={1000}>¥1000</option>
                  </select>
                </div>
              )}
            </div>

            {/* 給食基本セット（ベース） */}
            <div className="base-set-section">
              <div className="base-set-toggle">
                <label className={`base-set-checkbox ${baseSetEnabled ? 'active' : ''}`}>
                  <input
                    type="checkbox"
                    checked={baseSetEnabled}
                    onChange={(e) => setBaseSetEnabled(e.target.checked)}
                  />
                  <span className="checkmark" />
                  <span className="base-set-label">給食基本セット（固定量）</span>
                </label>
                <span className="base-set-desc">
                  米1合(150g) + 牛乳1パック(200g) + 納豆1パック(45g)
                </span>
              </div>
              {baseSetEnabled && (
                <div className="base-set-info">
                  <span className="base-food">米（精白米）: 150g固定</span>
                  <span className="base-food">牛乳: 200g固定</span>
                  <span className="base-food">納豆: 45g固定</span>
                </div>
              )}
            </div>

            {/* 定番料理テンプレート */}
            {recipes.length > 0 && (
              <div className="recipe-templates-section">
                <h3>定番料理から食材を追加</h3>
                <p className="recipe-templates-desc">料理名をクリックするとレシピ元サイトへ移動します</p>
                <div className="recipe-templates-grid">
                  {recipes.map(recipe => (
                    <div key={recipe.id} className="recipe-template-item">
                      <div className="recipe-template-header">
                        {recipe.source_url ? (
                          <a
                            href={recipe.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="recipe-name-link"
                            title={`${recipe.name}のレシピを見る`}
                          >
                            {recipe.name}
                          </a>
                        ) : (
                          <span className="recipe-name">{recipe.name}</span>
                        )}
                        <span className="recipe-servings">{recipe.servings}人分</span>
                      </div>
                      <div className="recipe-template-ingredients">
                        {recipe.ingredients.slice(0, 3).map((ing, i) => (
                          <span key={i} className={`ingredient-tag ${ing.matched_food ? 'matched' : 'unmatched'}`}>
                            {ing.original_name}
                          </span>
                        ))}
                        {recipe.ingredients.length > 3 && (
                          <span className="ingredient-more">+{recipe.ingredients.length - 3}</span>
                        )}
                      </div>
                      <button
                        className="recipe-add-btn"
                        onClick={() => applyRecipe(recipe)}
                        title="この料理の食材を追加"
                      >
                        追加
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* プリセットボタン */}
            <div className="preset-section">
              <h3>食材を追加選択</h3>
              <div className="preset-buttons">
                <button className="preset-btn all" onClick={() => applyPreset('all', true)}>
                  全部追加
                </button>
                <button className="preset-btn school" onClick={() => applyPreset('school_lunch', true)}>
                  給食定番
                </button>
                <button className="preset-btn school" onClick={() => applyPreset('school_bread', true)}>
                  パンセット
                </button>
                <button className="preset-btn" onClick={() => applyPreset('protein', true)}>
                  たんぱく源
                </button>
                <button className="preset-btn" onClick={() => applyPreset('vegetables', true)}>
                  野菜中心
                </button>
                <button className="preset-btn" onClick={() => applyPreset('fish', true)}>
                  魚介中心
                </button>
                <button className="preset-btn" onClick={() => applyPreset('budget', true)}>
                  節約食材
                </button>
                <button className="preset-btn clear" onClick={() => applyPreset('clear')}>
                  全解除
                </button>
              </div>
            </div>

            {/* 食材選択 */}
            <div className="food-selection">
              <div className="food-selection-header">
                <h3>食材を選択 ({selectedFoods.size}件{baseSetEnabled ? ` + 基本3件` : ''})</h3>
                <input
                  type="text"
                  placeholder="食材を検索..."
                  value={foodSearch}
                  onChange={e => setFoodSearch(e.target.value)}
                  className="food-search-input"
                />
              </div>

              {allFoods.length === 0 ? (
                <div className="loading-state">食材データを読み込み中...</div>
              ) : (
                <div className="food-grid">
                  {filteredFoods.map(food => {
                    const isSelected = selectedFoods.has(food.food_name);
                    const constraint = foodConstraints[food.food_name];
                    return (
                      <div
                        key={food.food_name}
                        className={`food-item ${isSelected ? 'selected' : ''} ${constraint ? 'has-constraint' : ''}`}
                      >
                        <div className="food-item-main" onClick={() => toggleFood(food.food_name)}>
                          <span className="food-name">{food.food_name}</span>
                          <span className="food-price-info">
                            {FOOD_DISPLAY_UNITS[food.food_name] ? (
                              <>
                                <span className="food-unit-price">
                                  ¥{Math.round(food.price_per_100g * FOOD_DISPLAY_UNITS[food.food_name].weight / 100)}/{FOOD_DISPLAY_UNITS[food.food_name].unit}
                                </span>
                                <span className="food-100g-price">({food.price_per_100g}/100g)</span>
                              </>
                            ) : (
                              <span className="food-100g-price">¥{food.price_per_100g}/100g</span>
                            )}
                          </span>
                          <span className="food-calories">{food.energy_kcal}kcal</span>
                        </div>
                        {isSelected && (
                          <div className="food-constraint">
                            {constraint ? (
                              <div className="constraint-display">
                                <span className="constraint-badge">
                                  {constraint.type === 'fixed' && `固定: ${constraint.fixed}g`}
                                  {constraint.type === 'min' && `最小: ${constraint.min}g`}
                                  {constraint.type === 'max' && `最大: ${constraint.max}g`}
                                  {constraint.type === 'unit' && `${constraint.unitCount}個 (${constraint.unitWeight}g×${constraint.unitCount}=${constraint.unitWeight! * constraint.unitCount!}g)`}
                                </span>
                                <button
                                  className="constraint-remove"
                                  onClick={(e) => { e.stopPropagation(); updateFoodConstraint(food.food_name, null); }}
                                >
                                  ×
                                </button>
                              </div>
                            ) : (
                              <div className="constraint-options">
                                {/* 単位指定ボタン（定義がある食材のみ） */}
                                {COMMON_UNIT_WEIGHTS[food.food_name] && (
                                  <select
                                    className="constraint-select"
                                    defaultValue=""
                                    onClick={(e) => e.stopPropagation()}
                                    onChange={(e) => {
                                      if (e.target.value) {
                                        const [weight, count] = e.target.value.split(':').map(Number);
                                        updateFoodConstraint(food.food_name, { type: 'unit', unitWeight: weight, unitCount: count });
                                      }
                                    }}
                                  >
                                    <option value="">個数指定...</option>
                                    {COMMON_UNIT_WEIGHTS[food.food_name].map(u => (
                                      [1, 2, 3].map(count => (
                                        <option key={`${u.name}-${count}`} value={`${u.weight}:${count}`}>
                                          {u.name} ×{count} ({u.weight * count}g)
                                        </option>
                                      ))
                                    )).flat()}
                                  </select>
                                )}
                                <button
                                  className="constraint-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    const amount = prompt('固定量（g）を入力:', '100');
                                    if (amount) updateFoodConstraint(food.food_name, { type: 'fixed', fixed: Number(amount) });
                                  }}
                                  title="固定量を設定"
                                >
                                  固定
                                </button>
                                <button
                                  className="constraint-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    const amount = prompt('最小量（g）を入力:', '50');
                                    if (amount) updateFoodConstraint(food.food_name, { type: 'min', min: Number(amount) });
                                  }}
                                  title="最小量を設定"
                                >
                                  最小
                                </button>
                                <button
                                  className="constraint-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    const amount = prompt('最大量（g）を入力:', '200');
                                    if (amount) updateFoodConstraint(food.food_name, { type: 'max', max: Number(amount) });
                                  }}
                                  title="最大量を設定"
                                >
                                  最大
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 制約付き食材一覧 */}
            {Object.keys(foodConstraints).length > 0 && (
              <div className="constraints-summary">
                <h4>量の指定がある食材</h4>
                <div className="constraints-list">
                  {Object.entries(foodConstraints).map(([name, c]) => (
                    <span key={name} className="constraint-tag">
                      {name}:
                      {c.type === 'fixed' && ` ${c.fixed}g固定`}
                      {c.type === 'min' && ` ${c.min}g以上`}
                      {c.type === 'max' && ` ${c.max}g以下`}
                      {c.type === 'unit' && ` ${c.unitCount}個(${c.unitWeight! * c.unitCount!}g)`}
                      <button onClick={() => updateFoodConstraint(name, null)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="calc-actions">
              <button
                className="calc-run-btn"
                onClick={() => runOptimization()}
                disabled={(selectedFoods.size === 0 && !baseSetEnabled) || calcLoading}
              >
                {calcLoading ? '計算中...' : '最適化計算を実行'}
              </button>
              {selectedFoods.size === 0 && !baseSetEnabled && (
                <span className="calc-hint">給食基本セットをONにするか、食材を選択してください</span>
              )}
              {baseSetEnabled && selectedFoods.size === 0 && (
                <span className="calc-hint base-only">給食基本セットのみで計算します</span>
              )}
            </div>

            {calcResult && (
              <div className="calc-result">
                {calcResult.success ? (
                  <>
                    <div className="calc-result-header">
                      <div className="result-cost">
                        <span className="label">最小コスト</span>
                        <span className="value">¥{Math.round(calcResult.total_cost)}</span>
                      </div>
                      <div className="result-weight">
                        <span className="label">食材数</span>
                        <span className="value">{calcResult.food_amounts.length}品</span>
                      </div>
                    </div>

                    <div className="calc-foods-table">
                      <div className="calc-foods-header">
                        <h4>必要な食材と量</h4>
                        {excludedFoods.size > 0 && (
                          <button className="recalc-btn" onClick={recalculateWithExclusions} disabled={calcLoading}>
                            {calcLoading ? '計算中...' : `${excludedFoods.size}品除外して再計算`}
                          </button>
                        )}
                      </div>
                      <table>
                        <thead>
                          <tr>
                            <th className="th-check">使用</th>
                            <th>食材</th>
                            <th>量</th>
                            <th>価格</th>
                          </tr>
                        </thead>
                        <tbody>
                          {calcResult.food_amounts.map(f => {
                            const isExcluded = excludedFoods.has(f.food_name);
                            return (
                              <tr key={f.food_name} className={isExcluded ? 'excluded' : ''}>
                                <td className="td-check">
                                  <input
                                    type="checkbox"
                                    checked={!isExcluded}
                                    onChange={() => toggleExcludeFood(f.food_name)}
                                    title={isExcluded ? 'クリックで再び使用' : 'クリックで除外'}
                                  />
                                </td>
                                <td className={isExcluded ? 'text-muted' : ''}>{f.food_name}</td>
                                <td className={isExcluded ? 'text-muted' : ''}>{Math.round(f.amount_g)}g</td>
                                <td className={isExcluded ? 'text-muted' : ''}>¥{Math.round(f.cost)}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                      {excludedFoods.size > 0 && (
                        <div className="excluded-info">
                          <span className="excluded-label">除外中:</span>
                          {Array.from(excludedFoods).map(name => (
                            <span key={name} className="excluded-tag">
                              {name}
                              <button onClick={() => toggleExcludeFood(name)}>×</button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="calc-nutrients">
                      <h4>栄養素達成率と食材貢献度</h4>
                      {/* 食材ごとに固定の色を割り当てる */}
                      {(() => {
                        const foodColors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#16a085', '#c0392b', '#8e44ad', '#27ae60', '#d35400'];
                        // calcResult.food_amounts の順番で色を割り当て（コスト順＝重要度順）
                        const foodColorMap: Record<string, string> = {};
                        calcResult.food_amounts.forEach((f, idx) => {
                          foodColorMap[f.food_name] = foodColors[idx % foodColors.length];
                        });
                        return (
                          <>
                          {/* 食材の色凡例 */}
                          <div className="food-color-legend">
                            {calcResult.food_amounts.map((f) => (
                              <span key={f.food_name} className="legend-item" style={{ borderColor: foodColorMap[f.food_name] }}>
                                <span className="legend-dot" style={{ backgroundColor: foodColorMap[f.food_name] }} />
                                {f.food_name}
                              </span>
                            ))}
                          </div>
                          <div className="nutrient-bars">
                            {calcResult.nutrients.map(n => (
                              <div key={n.name} className="nutrient-bar-row">
                                <div className="nutrient-bar-item">
                                  <span className="nutrient-label">{n.name}</span>
                                  <div className="nutrient-bar-bg-200">
                                    <div className="bar-100-mark" />
                                    {/* 貢献度を積み上げバーで表示 */}
                                    {n.contributions && n.contributions.length > 0 ? (
                                      <div className="stacked-bar">
                                        {n.contributions.map((c, idx) => {
                                          // 200%スケールなので percentage/2 を使用
                                          const width = Math.min(c.percentage / 2, 50);
                                          const left = n.contributions.slice(0, idx).reduce((sum, prev) => sum + Math.min(prev.percentage / 2, 50), 0);
                                          const color = foodColorMap[c.food_name] || '#999';
                                          return (
                                            <div
                                              key={c.food_name}
                                              className="stacked-segment"
                                              style={{
                                                left: `${left}%`,
                                                width: `${width}%`,
                                                backgroundColor: color,
                                              }}
                                              title={`${c.food_name}: ${c.contribution.toFixed(1)}${n.unit} (${c.percentage.toFixed(0)}%)`}
                                            />
                                          );
                                        })}
                                      </div>
                                    ) : (
                                      <div
                                        className={`nutrient-bar-fill ${n.ratio >= 100 ? (n.ratio > 150 ? 'excess' : 'complete') : n.ratio >= 80 ? 'near' : 'low'}`}
                                        style={{ width: `${Math.min(n.ratio / 2, 100)}%` }}
                                      />
                                    )}
                                  </div>
                                  <div className="nutrient-values">
                                    <span className="nutrient-actual">{n.actual.toFixed(1)}{n.unit}</span>
                                    <span className="nutrient-slash">/</span>
                                    <span className="nutrient-required">{n.required.toFixed(1)}{n.unit}</span>
                                    <span className={`nutrient-percent ${n.ratio >= 100 ? 'achieved' : ''}`}>({Math.round(n.ratio)}%)</span>
                                  </div>
                                </div>
                                {/* 貢献食材リスト */}
                                {n.contributions && n.contributions.length > 0 && (
                                  <div className="contribution-list">
                                    {n.contributions.slice(0, 4).map((c) => {
                                      const color = foodColorMap[c.food_name] || '#999';
                                      return (
                                        <span
                                          key={c.food_name}
                                          className="contribution-tag"
                                          style={{ borderColor: color, color: color }}
                                        >
                                          <span className="contrib-dot" style={{ backgroundColor: color }} />
                                          {c.food_name.length > 6 ? c.food_name.slice(0, 6) + '…' : c.food_name}
                                          <span className="contrib-pct">{Math.round(c.percentage)}%</span>
                                        </span>
                                      );
                                    })}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                          </>
                        );
                      })()}
                    </div>
                  </>
                ) : (
                  <div className="calc-error">
                    <p>{calcResult.message || '最適化に失敗しました。'}</p>
                    <p>より多くの食材を選択してみてください。</p>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>データ出典: 文部科学省「学校給食実施基準」、厚生労働省「日本人の食事摂取基準(2020年版)」、総務省「消費者物価指数」</p>
      </footer>
    </div>
  );
}
