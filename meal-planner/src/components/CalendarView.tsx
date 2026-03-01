import { useState, useEffect, useRef } from 'react';
import type { DailyMenu, SchoolGradeLevel } from '../types';
import { getMenuSlotNames } from '../types';
import type { useCalendar } from '../hooks/useCalendar';
import { analyzeDailyNutrition } from '../api';
import DayCell from './DayCell';

const WEEKDAYS = ['月', '火', '水', '木', '金'];

interface Props {
  calendar: ReturnType<typeof useCalendar>;
  dailyMenus: DailyMenu[];
  gradeLevel: SchoolGradeLevel;
  onDayClick: (date: string) => void;
  onSwitchToWeek: (date: string) => void;
}

export default function CalendarView({ calendar, dailyMenus, gradeLevel, onDayClick }: Props) {
  const menuMap = new Map(dailyMenus.map(dm => [dm.date, dm]));
  const [achievementMap, setAchievementMap] = useState<Map<string, number>>(new Map());
  const abortRef = useRef<AbortController | null>(null);

  // Batch nutrition analysis for menus that have content
  useEffect(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const menusWithContent = dailyMenus.filter(dm => {
      const names = getMenuSlotNames(dm.menu);
      return names.length > 0;
    });

    if (menusWithContent.length === 0) {
      setAchievementMap(new Map());
      return;
    }

    const promises = menusWithContent.map(dm =>
      analyzeDailyNutrition(dm.menu, gradeLevel)
        .then(result => ({ date: dm.date, rate: result.achievement_rate }))
        .catch(() => ({ date: dm.date, rate: 0 }))
    );

    Promise.all(promises).then(results => {
      if (controller.signal.aborted) return;
      const map = new Map<string, number>();
      for (const r of results) {
        map.set(r.date, r.rate);
      }
      setAchievementMap(map);
    });

    return () => { controller.abort(); };
  }, [dailyMenus, gradeLevel]);

  return (
    <div>
      <div className="calendar-header">
        <div className="calendar-nav">
          <button onClick={calendar.prevMonth}>&lt;</button>
          <span className="month-label">{calendar.monthLabel}</span>
          <button onClick={calendar.nextMonth}>&gt;</button>
        </div>
        <button onClick={calendar.goToToday} style={{ padding: '6px 12px', border: '1px solid #dfe6e9', borderRadius: 6, background: '#fff', cursor: 'pointer', fontSize: 13 }}>
          今日
        </button>
      </div>

      <div className="calendar-grid">
        {WEEKDAYS.map(w => (
          <div key={w} className="weekday-header">{w}</div>
        ))}
        {calendar.monthWeeks.flatMap(week =>
          week.map(date => {
            const dateMonth = parseInt(date.slice(5, 7), 10);
            const isCurrentMonth = dateMonth === calendar.month + 1;
            return (
              <DayCell
                key={date}
                date={date}
                dailyMenu={menuMap.get(date)}
                achievementRate={achievementMap.get(date) ?? null}
                isCurrentMonth={isCurrentMonth}
                onClick={onDayClick}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
