import { useState, useEffect, useCallback, useRef } from 'react';
import type { DailyMenuData, MealItem, FoodItem, Recipe, SchoolGradeLevel, MealSlotType, DailyNutritionResult, SubPlan } from '../types';
import { emptyMenu, getMonthFromDate } from '../types';
import MealSlot from './MealSlot';
import NutritionSummary from './NutritionSummary';
import SeasonalBadge from './SeasonalBadge';
import AllergenWarningPanel from './AllergenWarning';
import CostEstimate from './CostEstimate';
import CombinationCheck from './CombinationCheck';
import CookingEffort from './CookingEffort';
import SubPlanManager from './SubPlanManager';
import { analyzeDailyNutrition } from '../api';

const SLOTS: MealSlotType[] = ['staple', 'main_dish', 'side_dish', 'soup', 'dessert'];

interface Props {
  date: string;
  menu: DailyMenuData | null;
  gradeLevel: SchoolGradeLevel;
  recipes: Recipe[];
  foods: FoodItem[];
  planId: number;
  onSave: (date: string, menu: DailyMenuData) => Promise<void>;
  onClose: () => void;
}

export default function MenuEditor({ date, menu, gradeLevel, recipes, foods, planId, onSave, onClose }: Props) {
  const [editMenu, setEditMenu] = useState<DailyMenuData>(() =>
    menu ? JSON.parse(JSON.stringify(menu)) : emptyMenu()
  );
  const [nutrition, setNutrition] = useState<DailyNutritionResult | null>(null);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [currentSubPlan, setCurrentSubPlan] = useState<SubPlan | null>(null);
  const [activePanel, setActivePanel] = useState<'nutrition' | 'seasonal' | 'cost' | 'combination' | 'effort'>('nutrition');
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // 日付から月を取得
  const month = getMonthFromDate(date);

  // 除外アレルゲン（サブプランから取得）
  const excludedAllergens = currentSubPlan?.excluded_allergens || [];

  const updateSlot = useCallback((slot: MealSlotType, item: MealItem | null) => {
    setEditMenu(prev => ({ ...prev, [slot]: item }));
  }, []);

  const toggleMilk = useCallback(() => {
    setEditMenu(prev => ({ ...prev, milk: !prev.milk }));
  }, []);

  // Debounced nutrition analysis
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setNutritionLoading(true);
      try {
        const result = await analyzeDailyNutrition(editMenu, gradeLevel);
        setNutrition(result);
      } catch {
        setNutrition(null);
      } finally {
        setNutritionLoading(false);
      }
    }, 500);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [editMenu, gradeLevel]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(date, editMenu);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  const dateLabel = (() => {
    const d = new Date(date + 'T00:00:00');
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    return `${d.getMonth() + 1}月${d.getDate()}日（${weekdays[d.getDay()]}）`;
  })();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{dateLabel}の献立</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          {/* サブプラン管理 */}
          <SubPlanManager
            planId={planId}
            currentSubPlan={currentSubPlan}
            onSelect={setCurrentSubPlan}
          />

          {/* アレルゲン警告 */}
          <AllergenWarningPanel menu={editMenu} excludedAllergens={excludedAllergens} />

          <div className="editor-layout">
            <div className="meal-slots">
              {SLOTS.map(slot => (
                <MealSlot
                  key={slot}
                  slotType={slot}
                  item={editMenu[slot]}
                  foods={foods}
                  recipes={recipes}
                  onChange={(item) => updateSlot(slot, item)}
                />
              ))}
              <div className="milk-toggle">
                <input
                  type="checkbox"
                  id="milk-check"
                  checked={editMenu.milk}
                  onChange={toggleMilk}
                />
                <label htmlFor="milk-check">牛乳 (200ml)</label>
              </div>
            </div>

            <div className="analysis-panels">
              {/* パネル切替タブ */}
              <div className="panel-tabs">
                <button className={`panel-tab ${activePanel === 'nutrition' ? 'active' : ''}`} onClick={() => setActivePanel('nutrition')}>栄養</button>
                <button className={`panel-tab ${activePanel === 'cost' ? 'active' : ''}`} onClick={() => setActivePanel('cost')}>コスト</button>
                <button className={`panel-tab ${activePanel === 'seasonal' ? 'active' : ''}`} onClick={() => setActivePanel('seasonal')}>旬</button>
                <button className={`panel-tab ${activePanel === 'combination' ? 'active' : ''}`} onClick={() => setActivePanel('combination')}>食合せ</button>
                <button className={`panel-tab ${activePanel === 'effort' ? 'active' : ''}`} onClick={() => setActivePanel('effort')}>工数</button>
              </div>

              {/* パネル内容 */}
              {activePanel === 'nutrition' && (
                <NutritionSummary nutrition={nutrition} loading={nutritionLoading} />
              )}
              {activePanel === 'cost' && (
                <CostEstimate menu={editMenu} month={month} />
              )}
              {activePanel === 'seasonal' && (
                <SeasonalBadge menu={editMenu} month={month} />
              )}
              {activePanel === 'combination' && (
                <CombinationCheck menu={editMenu} />
              )}
              {activePanel === 'effort' && (
                <CookingEffort menu={editMenu} />
              )}
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button onClick={onClose}>キャンセル</button>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
