import { useState, useEffect, useCallback, useRef } from 'react';
import type { DailyMenuData, MealItem, FoodItem, Recipe, SchoolGradeLevel, MealSlotType, DailyNutritionResult } from '../types';
import { emptyMenu } from '../types';
import MealSlot from './MealSlot';
import NutritionSummary from './NutritionSummary';
import { analyzeDailyNutrition } from '../api';

const SLOTS: MealSlotType[] = ['staple', 'main_dish', 'side_dish', 'soup', 'dessert'];

interface Props {
  date: string;
  menu: DailyMenuData | null;
  gradeLevel: SchoolGradeLevel;
  recipes: Recipe[];
  foods: FoodItem[];
  onSave: (date: string, menu: DailyMenuData) => Promise<void>;
  onClose: () => void;
}

export default function MenuEditor({ date, menu, gradeLevel, recipes, foods, onSave, onClose }: Props) {
  const [editMenu, setEditMenu] = useState<DailyMenuData>(() =>
    menu ? JSON.parse(JSON.stringify(menu)) : emptyMenu()
  );
  const [nutrition, setNutrition] = useState<DailyNutritionResult | null>(null);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

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
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{dateLabel}の献立</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
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
            <NutritionSummary nutrition={nutrition} loading={nutritionLoading} />
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
