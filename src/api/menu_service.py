"""献立CRUD + 栄養分析サービス"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .menu_models import (
    DailyMenuData,
    DailyMenuResponse,
    DailyMenuUpdate,
    DailyNutritionResult,
    MenuCopyRequest,
    MenuPlanCreate,
    MenuPlanResponse,
    MenuPlanUpdate,
    NutrientResult,
    SchoolGradeLevel,
    WeeklyNutritionResult,
    GRADE_AGE_MAP,
)

from src.optimize import (
    calculate_totals,
    get_school_lunch_requirements,
    load_food_data,
    NUTRIENT_NAMES,
    NUTRIENT_UNITS,
)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "menus.db"

# 給食で追跡する主要栄養素（学校給食摂取基準に合致するもの）
TRACKED_NUTRIENTS = [
    "energy_kcal", "protein_g", "calcium_mg", "iron_mg",
    "vitamin_a_ug", "vitamin_b1_mg", "vitamin_b2_mg", "vitamin_c_mg",
    "fiber_g", "magnesium_mg", "zinc_mg",
]

# 牛乳の栄養価 (200ml = 約206g)
MILK_FOOD_NAME = "牛乳"
MILK_AMOUNT_G = 206.0


class MenuService:
    def __init__(self):
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS menu_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    grade_level TEXT NOT NULL DEFAULT 'elementary_mid',
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS daily_menus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    menu_json TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (plan_id) REFERENCES menu_plans(id) ON DELETE CASCADE,
                    UNIQUE(plan_id, date)
                );
            """)
            conn.commit()
        finally:
            conn.close()

    # --- Menu Plans CRUD ---

    def create_plan(self, req: MenuPlanCreate) -> MenuPlanResponse:
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "INSERT INTO menu_plans (name, grade_level, start_date, end_date) VALUES (?, ?, ?, ?)",
                (req.name, req.grade_level.value, req.start_date, req.end_date),
            )
            conn.commit()
            plan_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (plan_id,)).fetchone()
            return self._row_to_plan(row)
        finally:
            conn.close()

    def get_plans(self) -> list[MenuPlanResponse]:
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM menu_plans ORDER BY created_at DESC").fetchall()
            return [self._row_to_plan(r) for r in rows]
        finally:
            conn.close()

    def get_plan(self, plan_id: int) -> MenuPlanResponse | None:
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (plan_id,)).fetchone()
            return self._row_to_plan(row) if row else None
        finally:
            conn.close()

    def update_plan(self, plan_id: int, req: MenuPlanUpdate) -> MenuPlanResponse | None:
        conn = self._get_conn()
        try:
            existing = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (plan_id,)).fetchone()
            if not existing:
                return None
            name = req.name if req.name is not None else existing["name"]
            grade = req.grade_level.value if req.grade_level is not None else existing["grade_level"]
            start = req.start_date if req.start_date is not None else existing["start_date"]
            end = req.end_date if req.end_date is not None else existing["end_date"]
            conn.execute(
                "UPDATE menu_plans SET name=?, grade_level=?, start_date=?, end_date=? WHERE id=?",
                (name, grade, start, end, plan_id),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (plan_id,)).fetchone()
            return self._row_to_plan(row)
        finally:
            conn.close()

    def delete_plan(self, plan_id: int) -> bool:
        conn = self._get_conn()
        try:
            cursor = conn.execute("DELETE FROM menu_plans WHERE id = ?", (plan_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # --- Daily Menus ---

    def get_daily_menu(self, plan_id: int, date: str) -> DailyMenuResponse:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM daily_menus WHERE plan_id = ? AND date = ?",
                (plan_id, date),
            ).fetchone()
            if row:
                menu = DailyMenuData.model_validate_json(row["menu_json"])
            else:
                menu = DailyMenuData()
            return DailyMenuResponse(plan_id=plan_id, date=date, menu=menu)
        finally:
            conn.close()

    def update_daily_menu(self, req: DailyMenuUpdate) -> DailyMenuResponse:
        conn = self._get_conn()
        try:
            menu_json = req.menu.model_dump_json()
            conn.execute(
                """INSERT INTO daily_menus (plan_id, date, menu_json)
                   VALUES (?, ?, ?)
                   ON CONFLICT(plan_id, date) DO UPDATE SET menu_json = excluded.menu_json""",
                (req.plan_id, req.date, menu_json),
            )
            conn.commit()
            return DailyMenuResponse(plan_id=req.plan_id, date=req.date, menu=req.menu)
        finally:
            conn.close()

    def get_menus_range(self, plan_id: int, start_date: str, end_date: str) -> list[DailyMenuResponse]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM daily_menus WHERE plan_id = ? AND date >= ? AND date <= ? ORDER BY date",
                (plan_id, start_date, end_date),
            ).fetchall()
            result_map = {}
            for row in rows:
                menu = DailyMenuData.model_validate_json(row["menu_json"])
                result_map[row["date"]] = menu

            # 全平日分を返す（データなしの日は空メニュー）
            results = []
            current = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            while current <= end:
                if current.weekday() < 5:  # 月-金のみ
                    date_str = current.strftime("%Y-%m-%d")
                    menu = result_map.get(date_str, DailyMenuData())
                    results.append(DailyMenuResponse(plan_id=plan_id, date=date_str, menu=menu))
                current += timedelta(days=1)
            return results
        finally:
            conn.close()

    def copy_plan(self, req: MenuCopyRequest) -> MenuPlanResponse:
        conn = self._get_conn()
        try:
            source = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (req.source_plan_id,)).fetchone()
            if not source:
                raise ValueError(f"Plan {req.source_plan_id} not found")

            # 日数差を計算
            source_start = datetime.strptime(source["start_date"], "%Y-%m-%d")
            new_start = datetime.strptime(req.start_date, "%Y-%m-%d")
            delta = new_start - source_start
            source_end = datetime.strptime(source["end_date"], "%Y-%m-%d")
            new_end = source_end + delta

            cursor = conn.execute(
                "INSERT INTO menu_plans (name, grade_level, start_date, end_date) VALUES (?, ?, ?, ?)",
                (req.new_name, source["grade_level"], req.start_date, new_end.strftime("%Y-%m-%d")),
            )
            new_plan_id = cursor.lastrowid

            # 献立をコピー（日付をシフト）
            rows = conn.execute(
                "SELECT * FROM daily_menus WHERE plan_id = ?", (req.source_plan_id,)
            ).fetchall()
            for row in rows:
                old_date = datetime.strptime(row["date"], "%Y-%m-%d")
                new_date = old_date + delta
                conn.execute(
                    "INSERT INTO daily_menus (plan_id, date, menu_json) VALUES (?, ?, ?)",
                    (new_plan_id, new_date.strftime("%Y-%m-%d"), row["menu_json"]),
                )

            conn.commit()
            new_row = conn.execute("SELECT * FROM menu_plans WHERE id = ?", (new_plan_id,)).fetchone()
            return self._row_to_plan(new_row)
        finally:
            conn.close()

    # --- Nutrition Analysis ---

    def analyze_daily_nutrition(
        self, menu: DailyMenuData, grade_level: SchoolGradeLevel, date: str = ""
    ) -> DailyNutritionResult:
        """日別献立の栄養分析"""
        foods_df = load_food_data()
        age = GRADE_AGE_MAP[grade_level]
        standards = get_school_lunch_requirements(age)

        # 全食材を集約
        amounts: dict[str, float] = {}
        for slot in [menu.staple, menu.main_dish, menu.side_dish, menu.soup, menu.dessert]:
            if slot:
                for ing in slot.ingredients:
                    if ing.food_name and ing.amount_g > 0:
                        amounts[ing.food_name] = amounts.get(ing.food_name, 0) + ing.amount_g

        # 牛乳を追加
        if menu.milk:
            amounts[MILK_FOOD_NAME] = amounts.get(MILK_FOOD_NAME, 0) + MILK_AMOUNT_G

        # 栄養計算
        if amounts:
            totals = calculate_totals(foods_df, amounts)
        else:
            totals = {"total_cost": 0}

        # 基準と比較
        nutrients = []
        achieved_count = 0
        for key in TRACKED_NUTRIENTS:
            actual = totals.get(key, 0)
            standard = standards.get(key, 0)
            ratio = (actual / standard * 100) if standard > 0 else 0
            if ratio >= 80:
                achieved_count += 1
            nutrients.append(NutrientResult(
                key=key,
                name=NUTRIENT_NAMES.get(key, key),
                unit=NUTRIENT_UNITS.get(key, ""),
                actual=round(actual, 1),
                standard=round(standard, 1),
                ratio=round(ratio, 1),
            ))

        achievement_rate = round(achieved_count / len(TRACKED_NUTRIENTS) * 100, 1) if TRACKED_NUTRIENTS else 0

        return DailyNutritionResult(
            date=date,
            total_cost=round(totals.get("total_cost", 0), 0),
            nutrients=nutrients,
            achievement_rate=achievement_rate,
        )

    def analyze_weekly_nutrition(
        self, plan_id: int, start_date: str
    ) -> WeeklyNutritionResult:
        """週間栄養分析"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        grade_level = SchoolGradeLevel(plan.grade_level)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        # 月曜〜金曜
        end = start + timedelta(days=4)
        end_date = end.strftime("%Y-%m-%d")

        daily_menus = self.get_menus_range(plan_id, start_date, end_date)

        daily_results = []
        for dm in daily_menus:
            result = self.analyze_daily_nutrition(dm.menu, grade_level, dm.date)
            daily_results.append(result)

        # 週間平均を計算
        if daily_results:
            avg_nutrients = []
            for i, key in enumerate(TRACKED_NUTRIENTS):
                values = [dr.nutrients[i].actual for dr in daily_results if dr.nutrients]
                avg_val = sum(values) / len(values) if values else 0
                standard = daily_results[0].nutrients[i].standard if daily_results[0].nutrients else 0
                ratio = (avg_val / standard * 100) if standard > 0 else 0
                avg_nutrients.append(NutrientResult(
                    key=key,
                    name=NUTRIENT_NAMES.get(key, key),
                    unit=NUTRIENT_UNITS.get(key, ""),
                    actual=round(avg_val, 1),
                    standard=round(standard, 1),
                    ratio=round(ratio, 1),
                ))
            total_cost = sum(dr.total_cost for dr in daily_results)
            avg_achievement = sum(dr.achievement_rate for dr in daily_results) / len(daily_results)
        else:
            avg_nutrients = []
            total_cost = 0
            avg_achievement = 0

        return WeeklyNutritionResult(
            start_date=start_date,
            end_date=end_date,
            daily_results=daily_results,
            weekly_average=avg_nutrients,
            total_cost=round(total_cost, 0),
            average_achievement_rate=round(avg_achievement, 1),
        )

    # --- Helpers ---

    @staticmethod
    def _row_to_plan(row: sqlite3.Row) -> MenuPlanResponse:
        return MenuPlanResponse(
            id=row["id"],
            name=row["name"],
            grade_level=SchoolGradeLevel(row["grade_level"]),
            start_date=row["start_date"],
            end_date=row["end_date"],
            created_at=row["created_at"],
        )


menu_service = MenuService()
