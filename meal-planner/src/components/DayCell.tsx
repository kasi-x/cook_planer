import type { DailyMenu } from '../types';
import { getMenuSlotNames } from '../types';

interface Props {
  date: string;
  dailyMenu: DailyMenu | undefined;
  achievementRate: number | null;
  isCurrentMonth: boolean;
  onClick: (date: string) => void;
}

function isToday(dateStr: string): boolean {
  return dateStr === new Date().toISOString().slice(0, 10);
}

function getBadgeClass(rate: number): string {
  if (rate >= 80) return 'badge-green';
  if (rate >= 60) return 'badge-yellow';
  return 'badge-red';
}

export default function DayCell({ date, dailyMenu, achievementRate, isCurrentMonth, onClick }: Props) {
  const day = parseInt(date.slice(8, 10), 10);
  const menuData = dailyMenu?.menu;
  const names = menuData ? getMenuSlotNames(menuData) : [];
  const hasMenu = names.length > 0;

  return (
    <div
      className={`day-cell ${isCurrentMonth ? '' : 'other-month'}`}
      onClick={() => onClick(date)}
    >
      <div className={`day-number ${isToday(date) ? 'today' : ''}`}>
        {day}
      </div>
      {hasMenu && (
        <div className="menu-preview">
          {names.slice(0, 3).map((n, i) => (
            <div key={i} className="dish-name">{n}</div>
          ))}
          {names.length > 3 && <div className="dish-name">...</div>}
        </div>
      )}
      <div className={`achievement-badge ${
        achievementRate !== null ? getBadgeClass(achievementRate) : 'badge-gray'
      }`} />
    </div>
  );
}
