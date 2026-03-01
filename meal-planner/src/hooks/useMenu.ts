import { useState, useCallback } from 'react';
import type { MenuPlan, DailyMenu, DailyMenuData, SchoolGradeLevel } from '../types';
import * as api from '../api';

export function useMenu() {
  const [plans, setPlans] = useState<MenuPlan[]>([]);
  const [currentPlan, setCurrentPlan] = useState<MenuPlan | null>(null);
  const [dailyMenus, setDailyMenus] = useState<DailyMenu[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPlans = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.fetchMenuPlans();
      setPlans(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : '献立計画の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, []);

  const createPlan = useCallback(async (
    name: string,
    gradeLevel: SchoolGradeLevel,
    startDate: string,
    endDate: string,
  ) => {
    setError(null);
    try {
      const plan = await api.createMenuPlan({ name, grade_level: gradeLevel, start_date: startDate, end_date: endDate });
      setPlans(prev => [plan, ...prev]);
      setCurrentPlan(plan);
      return plan;
    } catch (e) {
      setError(e instanceof Error ? e.message : '献立計画の作成に失敗しました');
      throw e;
    }
  }, []);

  const selectPlan = useCallback((plan: MenuPlan) => {
    setCurrentPlan(plan);
    setError(null);
  }, []);

  const deletePlan = useCallback(async (planId: number) => {
    setError(null);
    try {
      await api.deleteMenuPlan(planId);
      setPlans(prev => prev.filter(p => p.id !== planId));
      if (currentPlan?.id === planId) {
        setCurrentPlan(null);
        setDailyMenus([]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '削除に失敗しました');
      throw e;
    }
  }, [currentPlan]);

  const loadMenusRange = useCallback(async (planId: number, start: string, end: string) => {
    setLoading(true);
    setError(null);
    try {
      const menus = await api.fetchMenusRange(planId, start, end);
      setDailyMenus(menus);
      return menus;
    } catch (e) {
      setError(e instanceof Error ? e.message : '献立データの読み込みに失敗しました');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const saveDailyMenu = useCallback(async (planId: number, date: string, menu: DailyMenuData) => {
    setError(null);
    try {
      const result = await api.updateDailyMenu(planId, date, menu);
      setDailyMenus(prev => {
        const exists = prev.some(dm => dm.date === date && dm.plan_id === planId);
        if (exists) {
          return prev.map(dm => (dm.date === date && dm.plan_id === planId) ? result : dm);
        }
        return [...prev, result].sort((a, b) => a.date.localeCompare(b.date));
      });
      return result;
    } catch (e) {
      setError(e instanceof Error ? e.message : '保存に失敗しました');
      throw e;
    }
  }, []);

  return {
    plans,
    currentPlan,
    dailyMenus,
    loading,
    error,
    loadPlans,
    createPlan,
    selectPlan,
    deletePlan,
    loadMenusRange,
    saveDailyMenu,
  };
}
