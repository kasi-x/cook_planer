import type { Gender, MealType } from '../types';

export interface Preset {
  id: string;
  name: string;
  description: string;
  fixedFoods: { name: string; amount: number }[];
  selectedFoods: string[];
  age?: number;
  gender?: Gender;
  mealType?: MealType;
}

// よくあるセットの定義
export const PRESETS: Preset[] = [
  {
    id: 'school_lunch',
    name: '小学校給食',
    description: '牛乳200ml + 米100gを固定、給食基準で計算',
    fixedFoods: [
      { name: '牛乳', amount: 200 },
      { name: '米（精白米）', amount: 100 },
    ],
    selectedFoods: [
      '鶏肉（むね）', '豚肉（もも）', 'さけ', 'さば',
      '豆腐（木綿）', '納豆',
      'キャベツ', 'にんじん', 'たまねぎ', 'ほうれんそう', 'ブロッコリー',
      'えのきたけ', 'しめじ',
      '味噌', '醤油',
    ],
    age: 10,
    gender: 'male',
    mealType: 'school_lunch',
  },
  {
    id: 'middle_school_lunch',
    name: '中学校給食',
    description: '牛乳200ml + 米150gを固定、給食基準で計算',
    fixedFoods: [
      { name: '牛乳', amount: 200 },
      { name: '米（精白米）', amount: 150 },
    ],
    selectedFoods: [
      '鶏肉（もも）', '豚肉（もも）', '牛肉（もも）', 'さけ', 'さば',
      '豆腐（木綿）', '納豆', '油揚げ',
      'キャベツ', 'にんじん', 'たまねぎ', 'ほうれんそう', 'ブロッコリー', 'じゃがいも',
      'えのきたけ', 'しめじ', 'まいたけ',
      '味噌', '醤油',
    ],
    age: 13,
    gender: 'male',
    mealType: 'school_lunch',
  },
  {
    id: 'japanese_breakfast',
    name: '和朝食',
    description: '米、味噌汁、卵、納豆など和食ベースの朝食',
    fixedFoods: [
      { name: '米（精白米）', amount: 150 },
      { name: '鶏卵（Ｌ）', amount: 60 },
    ],
    selectedFoods: [
      '納豆', '豆腐（木綿）',
      'だいこん', 'ねぎ', 'ほうれんそう', 'わかめ（乾燥）',
      '味噌', '醤油',
      'さけ', 'のり（焼き）',
    ],
    mealType: 'per_meal',
  },
  {
    id: 'western_breakfast',
    name: '洋朝食',
    description: 'パン、卵、牛乳など洋食ベースの朝食',
    fixedFoods: [
      { name: '食パン', amount: 80 },
      { name: '牛乳', amount: 200 },
      { name: '鶏卵（Ｌ）', amount: 60 },
    ],
    selectedFoods: [
      'バター', 'チーズ（プロセス）', 'ヨーグルト（プレーン）',
      'ハム（ロース）', 'ベーコン', 'ソーセージ',
      'トマト', 'レタス', 'きゅうり',
      'バナナ', 'りんご', 'キウイ',
    ],
    mealType: 'per_meal',
  },
  {
    id: 'protein_focus',
    name: 'たんぱく質重視',
    description: '肉・魚・大豆製品中心の高たんぱくメニュー',
    fixedFoods: [],
    selectedFoods: [
      '鶏肉（むね）', '鶏肉（ささみ）', '豚肉（もも）', '牛肉（もも）',
      'さけ', 'まぐろ（赤身）', 'さば', 'たら',
      '鶏卵（Ｌ）',
      '豆腐（木綿）', '納豆', '豆乳',
      'ヨーグルト（プレーン）', 'チーズ（プロセス）', '牛乳',
    ],
    mealType: 'daily',
  },
  {
    id: 'budget_meal',
    name: '節約献立',
    description: '安価な食材中心のコスパ重視メニュー',
    fixedFoods: [
      { name: '米（精白米）', amount: 200 },
    ],
    selectedFoods: [
      '鶏肉（むね）', '鶏肉（ひき肉）', '豚肉（ひき肉）',
      '鶏卵（Ｌ）',
      '豆腐（木綿）', '豆腐（絹ごし）', '納豆', '厚揚げ',
      'もやし', 'キャベツ', 'たまねぎ', 'にんじん', 'じゃがいも',
      'えのきたけ', 'しめじ',
      '牛乳',
    ],
    mealType: 'daily',
  },
  {
    id: 'vegetarian',
    name: '肉なし献立',
    description: '魚・大豆製品・野菜中心のメニュー',
    fixedFoods: [],
    selectedFoods: [
      'さけ', 'さば', 'あじ', 'いわし',
      '鶏卵（Ｌ）',
      '豆腐（木綿）', '豆腐（絹ごし）', '納豆', '油揚げ', '厚揚げ', '豆乳',
      '牛乳', 'ヨーグルト（プレーン）', 'チーズ（プロセス）',
      'キャベツ', 'ほうれんそう', 'ブロッコリー', 'にんじん', 'たまねぎ', 'トマト',
      'しいたけ（生）', 'えのきたけ', 'しめじ', 'まいたけ', 'エリンギ',
      'わかめ（乾燥）', 'ひじき（乾燥）',
    ],
    mealType: 'daily',
  },
  {
    id: 'elementary_low_lunch',
    name: '小学校低学年給食',
    description: '6-7歳向け。牛乳200ml + 米80g固定',
    fixedFoods: [
      { name: '牛乳', amount: 200 },
      { name: '米（精白米）', amount: 80 },
    ],
    selectedFoods: [
      '鶏肉（むね）', '豚肉（もも）', 'さけ',
      '豆腐（木綿）', '納豆',
      'キャベツ', 'にんじん', 'たまねぎ', 'ほうれんそう',
      'えのきたけ', 'しめじ',
      '味噌', '醤油',
    ],
    age: 7,
    gender: 'male',
    mealType: 'school_lunch',
  },
  {
    id: 'toddler_meal',
    name: '幼児食（3-5歳）',
    description: '小さな子供向けの栄養バランス食',
    fixedFoods: [
      { name: '牛乳', amount: 200 },
      { name: '米（精白米）', amount: 80 },
    ],
    selectedFoods: [
      '鶏肉（むね）', '鶏肉（ささみ）', 'さけ', 'たら',
      '鶏卵（Ｌ）',
      '豆腐（絹ごし）', '納豆',
      'にんじん', 'ほうれんそう', 'ブロッコリー', 'じゃがいも',
      'バナナ', 'りんご',
      'ヨーグルト（プレーン）',
    ],
    age: 4,
    gender: 'male',
    mealType: 'daily',
  },
  {
    id: 'senior_healthy',
    name: '高齢者健康食',
    description: '65歳以上向け。たんぱく質・カルシウム重視',
    fixedFoods: [
      { name: '牛乳', amount: 200 },
    ],
    selectedFoods: [
      '鶏肉（むね）', '鶏肉（ささみ）', 'さけ', 'さば', 'たら',
      '鶏卵（Ｌ）',
      '豆腐（木綿）', '納豆', '豆乳',
      'ほうれんそう', 'ブロッコリー', 'にんじん', 'キャベツ',
      'しいたけ（生）', 'しめじ',
      'ヨーグルト（プレーン）', 'チーズ（プロセス）',
      'わかめ（乾燥）', 'ひじき（乾燥）',
    ],
    age: 70,
    gender: 'male',
    mealType: 'daily',
  },
];

interface Props {
  onApplyPreset: (preset: Preset) => void;
}

export function PresetSelector({ onApplyPreset }: Props) {
  return (
    <section className="panel preset-selector">
      <h2>よくあるセット</h2>
      <p className="hint">ワンクリックで食材・設定を一括選択</p>
      <div className="preset-grid">
        {PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className="preset-btn"
            onClick={() => onApplyPreset(preset)}
          >
            <span className="preset-name">{preset.name}</span>
            <span className="preset-desc">{preset.description}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
