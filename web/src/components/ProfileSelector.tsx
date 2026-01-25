import type { Gender, MealType } from '../types';
import { GENDER_LABELS, MEAL_TYPE_LABELS } from '../types';

// 年齢グループの定義（バックエンドと同期）
const AGE_GROUPS = [
  { min: 1, max: 2, label: '1-2歳' },
  { min: 3, max: 5, label: '3-5歳' },
  { min: 6, max: 7, label: '6-7歳' },
  { min: 8, max: 9, label: '8-9歳' },
  { min: 10, max: 11, label: '10-11歳' },
  { min: 12, max: 14, label: '12-14歳' },
  { min: 15, max: 17, label: '15-17歳' },
  { min: 18, max: 29, label: '18-29歳' },
  { min: 30, max: 49, label: '30-49歳' },
  { min: 50, max: 64, label: '50-64歳' },
  { min: 65, max: 74, label: '65-74歳' },
  { min: 75, max: 120, label: '75歳以上' },
];

function getAgeGroupLabel(age: number): string {
  const group = AGE_GROUPS.find(g => age >= g.min && age <= g.max);
  return group?.label ?? '不明';
}

interface Props {
  age: number;
  gender: Gender;
  mealType: MealType;
  onAgeChange: (age: number) => void;
  onGenderChange: (gender: Gender) => void;
  onMealTypeChange: (mealType: MealType) => void;
}

export function ProfileSelector({
  age,
  gender,
  mealType,
  onAgeChange,
  onGenderChange,
  onMealTypeChange,
}: Props) {
  // 給食基準の場合は年齢・性別を非表示
  const showAgeGender = mealType !== 'school_lunch';

  const handleAgeInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= 120) {
      onAgeChange(value);
    }
  };

  return (
    <section className="panel profile-panel">
      <h2>計算設定</h2>

      <div className="profile-inputs">
        <div className="profile-field">
          <label>計算単位</label>
          <div className="meal-type-options">
            {(Object.keys(MEAL_TYPE_LABELS) as MealType[]).map((m) => (
              <label key={m} className={`meal-type-option ${mealType === m ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="mealType"
                  value={m}
                  checked={mealType === m}
                  onChange={() => onMealTypeChange(m)}
                />
                <span>{MEAL_TYPE_LABELS[m]}</span>
              </label>
            ))}
          </div>
        </div>

        {showAgeGender && (
          <>
            <div className="profile-field">
              <label>年齢</label>
              <div className="age-input-group">
                <input
                  type="number"
                  min={1}
                  max={120}
                  value={age}
                  onChange={handleAgeInputChange}
                />
                <span className="age-unit">歳</span>
                <span className="age-group-label">（{getAgeGroupLabel(age)}）</span>
              </div>
            </div>

            <div className="profile-field">
              <label>性別</label>
              <div className="gender-options">
                {(Object.keys(GENDER_LABELS) as Gender[]).map((g) => (
                  <label key={g} className={`gender-option ${gender === g ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="gender"
                      value={g}
                      checked={gender === g}
                      onChange={() => onGenderChange(g)}
                    />
                    <span>{GENDER_LABELS[g]}</span>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
