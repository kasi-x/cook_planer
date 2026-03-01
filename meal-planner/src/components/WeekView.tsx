import type { DailyMenu, SchoolGradeLevel } from '../types';
import { MEAL_SLOT_LABELS } from '../types';
import type { MealSlotType } from '../types';
import type { useCalendar } from '../hooks/useCalendar';

const WEEKDAY_NAMES = ['月', '火', '水', '木', '金'];
const SLOTS: MealSlotType[] = ['staple', 'main_dish', 'side_dish', 'soup', 'dessert'];

interface Props {
  calendar: ReturnType<typeof useCalendar>;
  dailyMenus: DailyMenu[];
  gradeLevel: SchoolGradeLevel;
  onDayClick: (date: string) => void;
  onBackToMonth: () => void;
}

export default function WeekView({ calendar, dailyMenus, onDayClick, onBackToMonth }: Props) {
  const menuMap = new Map(dailyMenus.map(dm => [dm.date, dm]));

  return (
    <div className="week-view">
      <div className="calendar-header">
        <div className="calendar-nav">
          <button onClick={calendar.prevWeek}>&lt;</button>
          <span className="month-label">{calendar.weekLabel}</span>
          <button onClick={calendar.nextWeek}>&gt;</button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={calendar.goToToday} style={{ padding: '6px 12px', border: '1px solid #dfe6e9', borderRadius: 6, background: '#fff', cursor: 'pointer', fontSize: 13 }}>
            今週
          </button>
          <button onClick={onBackToMonth} style={{ padding: '6px 12px', border: '1px solid #dfe6e9', borderRadius: 6, background: '#fff', cursor: 'pointer', fontSize: 13 }}>
            月表示
          </button>
        </div>
      </div>

      <div className="week-grid">
        {calendar.currentWeekDates.map((date, idx) => {
          const dm = menuMap.get(date);
          const day = parseInt(date.slice(8, 10), 10);
          return (
            <div key={date} className="week-day-card" onClick={() => onDayClick(date)}>
              <div className="day-header">
                {WEEKDAY_NAMES[idx]} {day}日
              </div>
              <div className="slot-list">
                {SLOTS.map(slot => {
                  const item = dm?.menu?.[slot];
                  return (
                    <div key={slot} className="slot-item">
                      <span className="slot-label">{MEAL_SLOT_LABELS[slot]}:</span>
                      <span className="slot-value">{item?.name || '-'}</span>
                    </div>
                  );
                })}
                <div className="slot-item">
                  <span className="slot-label">牛乳:</span>
                  <span className="slot-value">{dm?.menu?.milk !== false ? 'あり' : 'なし'}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
