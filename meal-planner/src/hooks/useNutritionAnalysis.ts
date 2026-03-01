import { useState, useCallback } from 'react';
import type { DailyMenuData, DailyNutritionResult, WeeklyNutritionResult, SchoolGradeLevel } from '../types';
import * as api from '../api';

export function useNutritionAnalysis() {
  const [dailyNutrition, setDailyNutrition] = useState<DailyNutritionResult | null>(null);
  const [weeklyNutrition, setWeeklyNutrition] = useState<WeeklyNutritionResult | null>(null);
  const [loading, setLoading] = useState(false);

  const analyzeDaily = useCallback(async (menu: DailyMenuData, gradeLevel: SchoolGradeLevel) => {
    setLoading(true);
    try {
      const result = await api.analyzeDailyNutrition(menu, gradeLevel);
      setDailyNutrition(result);
      return result;
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeWeekly = useCallback(async (planId: number, startDate: string) => {
    setLoading(true);
    try {
      const result = await api.analyzeWeeklyNutrition(planId, startDate);
      setWeeklyNutrition(result);
      return result;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    dailyNutrition,
    weeklyNutrition,
    loading,
    analyzeDaily,
    analyzeWeekly,
  };
}
