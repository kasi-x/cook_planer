import { useState, useMemo, useCallback } from 'react';

function getMonday(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  d.setDate(diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

function formatDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function addDays(d: Date, n: number): Date {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

export type CalendarMode = 'month' | 'week';

export interface WeekDays {
  monday: string;
  tuesday: string;
  wednesday: string;
  thursday: string;
  friday: string;
}

export function useCalendar() {
  const [mode, setMode] = useState<CalendarMode>('month');
  const [currentDate, setCurrentDate] = useState(() => new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthWeeks = useMemo(() => {
    const weeks: string[][] = [];
    const first = new Date(year, month, 1);
    let monday = getMonday(first);

    // Keep generating weeks until we pass the end of month
    const lastDay = new Date(year, month + 1, 0);
    lastDay.setHours(0, 0, 0, 0);
    while (monday <= lastDay) {
      const week: string[] = [];
      for (let i = 0; i < 5; i++) {
        week.push(formatDate(addDays(monday, i)));
      }
      weeks.push(week);
      monday = addDays(monday, 7);
    }
    return weeks;
  }, [year, month]);

  const currentWeekDates = useMemo(() => {
    const monday = getMonday(currentDate);
    return Array.from({ length: 5 }, (_, i) => formatDate(addDays(monday, i)));
  }, [currentDate]);

  const monthStart = useMemo(() => formatDate(new Date(year, month, 1)), [year, month]);
  const monthEnd = useMemo(() => formatDate(new Date(year, month + 1, 0)), [year, month]);

  const weekStart = useMemo(() => {
    const monday = getMonday(currentDate);
    return formatDate(monday);
  }, [currentDate]);
  const weekEnd = useMemo(() => {
    const monday = getMonday(currentDate);
    return formatDate(addDays(monday, 4));
  }, [currentDate]);

  const prevMonth = useCallback(() => {
    setCurrentDate(new Date(year, month - 1, 1));
  }, [year, month]);

  const nextMonth = useCallback(() => {
    setCurrentDate(new Date(year, month + 1, 1));
  }, [year, month]);

  const prevWeek = useCallback(() => {
    setCurrentDate(prev => addDays(prev, -7));
  }, []);

  const nextWeek = useCallback(() => {
    setCurrentDate(prev => addDays(prev, 7));
  }, []);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  const monthLabel = `${year}年${month + 1}月`;

  const weekLabel = useMemo(() => {
    const monday = getMonday(currentDate);
    const friday = addDays(monday, 4);
    return `${monday.getMonth() + 1}/${monday.getDate()} - ${friday.getMonth() + 1}/${friday.getDate()}`;
  }, [currentDate]);

  return {
    mode,
    setMode,
    currentDate,
    year,
    month,
    monthWeeks,
    currentWeekDates,
    monthStart,
    monthEnd,
    weekStart,
    weekEnd,
    prevMonth,
    nextMonth,
    prevWeek,
    nextWeek,
    goToToday,
    monthLabel,
    weekLabel,
  };
}
