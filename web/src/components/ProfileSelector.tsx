import type { Gender, MealType } from '../types';
import { GENDER_LABELS, MEAL_TYPE_LABELS } from '../types';

const AGE_OPTIONS = [
  { value: 15, label: '15歳' },
  { value: 23, label: '23歳' },
];

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
              <div className="age-options">
                {AGE_OPTIONS.map((opt) => (
                  <label key={opt.value} className={`age-option ${age === opt.value ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="age"
                      value={opt.value}
                      checked={age === opt.value}
                      onChange={() => onAgeChange(opt.value)}
                    />
                    <span>{opt.label}</span>
                  </label>
                ))}
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
