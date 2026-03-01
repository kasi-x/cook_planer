import { useState, useEffect } from 'react';
import type { WeeklyNutritionResult } from '../types';
import type { useCalendar } from '../hooks/useCalendar';
import { analyzeWeeklyNutrition } from '../api';

const WEEKDAY_NAMES = ['月', '火', '水', '木', '金'];

interface Props {
  planId: number;
  calendar: ReturnType<typeof useCalendar>;
}

export default function WeeklyReport({ planId, calendar }: Props) {
  const [report, setReport] = useState<WeeklyNutritionResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    analyzeWeeklyNutrition(planId, calendar.weekStart)
      .then(setReport)
      .catch(() => setReport(null))
      .finally(() => setLoading(false));
  }, [planId, calendar.weekStart]);

  return (
    <div className="weekly-report">
      <div className="report-header">
        <div className="calendar-nav">
          <button onClick={calendar.prevWeek}>&lt;</button>
          <span className="month-label">{calendar.weekLabel}</span>
          <button onClick={calendar.nextWeek}>&gt;</button>
        </div>
      </div>

      {loading && <p style={{ color: '#636e72', textAlign: 'center', padding: 40 }}>読み込み中...</p>}

      {!loading && report && (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table className="report-table">
              <thead>
                <tr>
                  <th>栄養素</th>
                  <th>基準値</th>
                  {report.daily_results.map((dr, idx) => (
                    <th key={dr.date}>{WEEKDAY_NAMES[idx]}</th>
                  ))}
                  <th>平均</th>
                </tr>
              </thead>
              <tbody>
                {report.weekly_average.map((avg, nIdx) => (
                  <tr key={avg.key}>
                    <td>{avg.name} ({avg.unit})</td>
                    <td className="standard-row">{avg.standard}</td>
                    {report.daily_results.map(dr => {
                      const n = dr.nutrients[nIdx];
                      if (!n) return <td key={dr.date}>-</td>;
                      const cls = n.ratio >= 80 ? 'meets-standard' : 'below-standard';
                      return <td key={dr.date} className={cls}>{n.actual}</td>;
                    })}
                    <td className={`average-row ${avg.ratio >= 80 ? 'meets-standard' : 'below-standard'}`}>
                      {avg.actual}
                    </td>
                  </tr>
                ))}
                <tr style={{ fontWeight: 600 }}>
                  <td>食材費 (円)</td>
                  <td>-</td>
                  {report.daily_results.map(dr => (
                    <td key={dr.date}>&yen;{dr.total_cost}</td>
                  ))}
                  <td className="average-row">
                    &yen;{report.daily_results.length > 0
                      ? Math.round(report.total_cost / report.daily_results.length)
                      : 0}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="report-total-cost">
            週間合計: &yen;{report.total_cost} / 平均達成率: {report.average_achievement_rate}%
          </div>
        </>
      )}

      {!loading && !report && (
        <p style={{ color: '#636e72', textAlign: 'center', padding: 40 }}>
          この週のデータがありません
        </p>
      )}
    </div>
  );
}
