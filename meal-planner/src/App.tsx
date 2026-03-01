import { useState, useEffect, useCallback } from 'react';
import { useMenu } from './hooks/useMenu';
import { useCalendar } from './hooks/useCalendar';
import { useRecipes } from './hooks/useRecipes';
import PlanSelector from './components/PlanSelector';
import GradeSelector from './components/GradeSelector';
import CalendarView from './components/CalendarView';
import WeekView from './components/WeekView';
import MenuEditor from './components/MenuEditor';
import WeeklyReport from './components/WeeklyReport';
import { updateMenuPlan } from './api';
import type { DailyMenuData, SchoolGradeLevel } from './types';

type Tab = 'calendar' | 'report';

export default function App() {
  const [tab, setTab] = useState<Tab>('calendar');
  const [editingDate, setEditingDate] = useState<string | null>(null);

  const menu = useMenu();
  const calendar = useCalendar();
  const { recipes, foods } = useRecipes();

  // Load plans on mount
  useEffect(() => {
    menu.loadPlans();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load menus when plan or month changes
  useEffect(() => {
    if (menu.currentPlan) {
      menu.loadMenusRange(menu.currentPlan.id, calendar.monthStart, calendar.monthEnd);
    }
  }, [menu.currentPlan?.id, calendar.monthStart, calendar.monthEnd]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDayClick = useCallback((date: string) => {
    setEditingDate(date);
  }, []);

  const handleEditorClose = useCallback(() => {
    setEditingDate(null);
  }, []);

  const handleSaveMenu = useCallback(async (date: string, menuData: DailyMenuData) => {
    if (!menu.currentPlan) return;
    await menu.saveDailyMenu(menu.currentPlan.id, date, menuData);
  }, [menu]);

  const handleGradeChange = useCallback(async (grade: SchoolGradeLevel) => {
    if (!menu.currentPlan) return;
    const updated = await updateMenuPlan(menu.currentPlan.id, { grade_level: grade });
    menu.selectPlan(updated);
  }, [menu]);

  const editingMenu = editingDate
    ? menu.dailyMenus.find(dm => dm.date === editingDate)?.menu ?? null
    : null;

  return (
    <div className="app">
      <header className="app-header">
        <h1>給食献立作成支援</h1>
        <div className="header-controls">
          <PlanSelector
            plans={menu.plans}
            currentPlan={menu.currentPlan}
            onSelect={menu.selectPlan}
            onCreate={menu.createPlan}
            onDelete={menu.deletePlan}
          />
          {menu.currentPlan && (
            <GradeSelector
              value={menu.currentPlan.grade_level}
              onChange={handleGradeChange}
            />
          )}
        </div>
      </header>

      {menu.currentPlan ? (
        <>
          {menu.error && (
            <div style={{ padding: '10px 16px', background: '#ffeaea', color: '#e17055', borderRadius: 8, marginBottom: 12, fontSize: 13 }}>
              {menu.error}
            </div>
          )}
          <nav className="tab-nav">
            <button
              className={`tab-btn ${tab === 'calendar' ? 'active' : ''}`}
              onClick={() => setTab('calendar')}
            >
              カレンダー
            </button>
            <button
              className={`tab-btn ${tab === 'report' ? 'active' : ''}`}
              onClick={() => setTab('report')}
            >
              週間レポート
            </button>
          </nav>

          <main className="app-main">
            {tab === 'calendar' && (
              <>
                {calendar.mode === 'month' ? (
                  <CalendarView
                    calendar={calendar}
                    dailyMenus={menu.dailyMenus}
                    gradeLevel={menu.currentPlan.grade_level}
                    onDayClick={handleDayClick}
                    onSwitchToWeek={() => {
                      calendar.setMode('week');
                    }}
                  />
                ) : (
                  <WeekView
                    calendar={calendar}
                    dailyMenus={menu.dailyMenus}
                    gradeLevel={menu.currentPlan.grade_level}
                    onDayClick={handleDayClick}
                    onBackToMonth={() => calendar.setMode('month')}
                  />
                )}
              </>
            )}

            {tab === 'report' && (
              <WeeklyReport
                planId={menu.currentPlan.id}
                calendar={calendar}
              />
            )}
          </main>

          {editingDate && (
            <MenuEditor
              date={editingDate}
              menu={editingMenu}
              gradeLevel={menu.currentPlan.grade_level}
              recipes={recipes}
              foods={foods}
              onSave={handleSaveMenu}
              onClose={handleEditorClose}
            />
          )}
        </>
      ) : (
        <div className="empty-state">
          <p>献立計画を選択または新規作成してください</p>
        </div>
      )}
    </div>
  );
}
