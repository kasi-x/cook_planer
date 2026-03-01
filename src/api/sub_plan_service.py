"""サブプラン管理サービス

アレルギー対応等で特定の児童向けに代替献立を管理する。
親プランの献立をベースに、特定スロットのみオーバーライドする。
"""

import json
import sqlite3
from pathlib import Path
from .menu_models import DailyMenuData, MealItem
from .allergy_service import check_allergens, filter_foods_by_allergens

DB_PATH = Path(__file__).parent.parent.parent / "data" / "menus.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_sub_plan(parent_plan_id: int, name: str, description: str = "", excluded_allergens: list[str] | None = None) -> dict:
    """サブプラン作成"""
    allergens = excluded_allergens or []
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "INSERT INTO sub_plans (parent_plan_id, name, description, allergen_profile_json) VALUES (?, ?, ?, ?)",
            (parent_plan_id, name, description, json.dumps(allergens, ensure_ascii=False)),
        )
        conn.commit()
        sub_plan_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM sub_plans WHERE id = ?", (sub_plan_id,)).fetchone()
        return _row_to_sub_plan(row)
    finally:
        conn.close()


def get_sub_plans(parent_plan_id: int) -> list[dict]:
    """親プランに紐づくサブプラン一覧"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM sub_plans WHERE parent_plan_id = ? ORDER BY created_at",
            (parent_plan_id,),
        ).fetchall()
        return [_row_to_sub_plan(r) for r in rows]
    finally:
        conn.close()


def get_sub_plan(sub_plan_id: int) -> dict | None:
    """サブプラン取得"""
    conn = _get_conn()
    try:
        row = conn.execute("SELECT * FROM sub_plans WHERE id = ?", (sub_plan_id,)).fetchone()
        return _row_to_sub_plan(row) if row else None
    finally:
        conn.close()


def delete_sub_plan(sub_plan_id: int) -> bool:
    """サブプラン削除"""
    conn = _get_conn()
    try:
        cursor = conn.execute("DELETE FROM sub_plans WHERE id = ?", (sub_plan_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def set_override(sub_plan_id: int, date: str, slot: str, item: dict) -> dict:
    """特定日・スロットの代替食材を設定"""
    conn = _get_conn()
    try:
        item_json = json.dumps(item, ensure_ascii=False)
        conn.execute(
            """INSERT INTO sub_plan_overrides (sub_plan_id, date, slot, override_item_json)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(sub_plan_id, date, slot) DO UPDATE SET override_item_json = excluded.override_item_json""",
            (sub_plan_id, date, slot, item_json),
        )
        conn.commit()
        return {"sub_plan_id": sub_plan_id, "date": date, "slot": slot, "item": item}
    finally:
        conn.close()


def get_overrides(sub_plan_id: int, date: str) -> dict[str, dict]:
    """特定日のオーバーライド一覧"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM sub_plan_overrides WHERE sub_plan_id = ? AND date = ?",
            (sub_plan_id, date),
        ).fetchall()
        return {row["slot"]: json.loads(row["override_item_json"]) for row in rows}
    finally:
        conn.close()


def get_sub_plan_menu(sub_plan_id: int, date: str, parent_menu: DailyMenuData) -> dict:
    """親プランの献立にオーバーライドを適用したサブプランメニューを返す"""
    overrides = get_overrides(sub_plan_id, date)

    # 親メニューをdictに変換
    menu_dict = parent_menu.model_dump()

    # オーバーライドを適用
    for slot, override_item in overrides.items():
        if slot in menu_dict:
            menu_dict[slot] = override_item

    return {
        "sub_plan_id": sub_plan_id,
        "date": date,
        "menu": menu_dict,
        "overrides": overrides,
    }


def auto_suggest_alternatives(parent_menu: DailyMenuData, excluded_allergens: list[str]) -> list[dict]:
    """アレルゲンフリー代替候補を自動提案"""
    warnings = check_allergens(parent_menu, excluded_allergens)
    suggestions: list[dict] = []

    # 代替食材の簡易マッピング
    ALTERNATIVES = {
        "乳": {"牛乳": "豆乳", "チーズ": "豆腐", "バター": "サラダ油", "ヨーグルト": "豆乳"},
        "卵": {"鶏卵": "豆腐", "マヨネーズ": ""},
        "小麦": {"パン": "米（精白米）", "うどん": "米（精白米）", "スパゲッティ": "米（精白米）"},
        "えび": {"えび": "鶏肉"},
        "そば": {"そば": "うどん"},
    }

    for warning in warnings:
        allergen = warning["allergen"]
        source_food = warning["source_food"]
        slot = warning["slot"]

        alternative = ""
        if allergen in ALTERNATIVES:
            for keyword, alt in ALTERNATIVES[allergen].items():
                if keyword in source_food:
                    alternative = alt
                    break

        suggestions.append({
            "slot": slot,
            "original_food": source_food,
            "allergen": allergen,
            "alternative": alternative,
            "reason": f"{allergen}アレルギー対応",
        })

    return suggestions


def _row_to_sub_plan(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "parent_plan_id": row["parent_plan_id"],
        "name": row["name"],
        "description": row["description"],
        "excluded_allergens": json.loads(row["allergen_profile_json"]),
        "created_at": row["created_at"],
    }
