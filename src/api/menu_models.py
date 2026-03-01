"""献立作成支援のPydanticモデル"""

from enum import Enum
from pydantic import BaseModel, Field


class SchoolGradeLevel(str, Enum):
    """学年区分"""
    ELEMENTARY_LOW = "elementary_low"    # 小学校低学年 (6-7歳)
    ELEMENTARY_MID = "elementary_mid"    # 小学校中学年 (8-9歳)
    ELEMENTARY_HIGH = "elementary_high"  # 小学校高学年 (10-11歳)
    JUNIOR_HIGH = "junior_high"         # 中学校 (12-14歳)


GRADE_AGE_MAP = {
    SchoolGradeLevel.ELEMENTARY_LOW: 7,
    SchoolGradeLevel.ELEMENTARY_MID: 9,
    SchoolGradeLevel.ELEMENTARY_HIGH: 11,
    SchoolGradeLevel.JUNIOR_HIGH: 13,
}

GRADE_LABELS = {
    SchoolGradeLevel.ELEMENTARY_LOW: "小学校低学年",
    SchoolGradeLevel.ELEMENTARY_MID: "小学校中学年",
    SchoolGradeLevel.ELEMENTARY_HIGH: "小学校高学年",
    SchoolGradeLevel.JUNIOR_HIGH: "中学校",
}


# --- Request / Response Models ---

class MealIngredient(BaseModel):
    """食材"""
    food_name: str
    amount_g: float = Field(ge=0)


class MealItem(BaseModel):
    """料理（1スロット分）"""
    name: str
    recipe_id: str | None = None
    ingredients: list[MealIngredient] = Field(default_factory=list)


class DailyMenuData(BaseModel):
    """日別献立データ（リクエスト用）"""
    staple: MealItem | None = None       # 主食
    main_dish: MealItem | None = None    # 主菜
    side_dish: MealItem | None = None    # 副菜
    soup: MealItem | None = None         # 汁物
    dessert: MealItem | None = None      # デザート
    milk: bool = True                    # 牛乳


class MenuPlanCreate(BaseModel):
    """献立計画作成リクエスト"""
    name: str
    grade_level: SchoolGradeLevel = SchoolGradeLevel.ELEMENTARY_MID
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD


class MenuPlanUpdate(BaseModel):
    """献立計画更新リクエスト"""
    name: str | None = None
    grade_level: SchoolGradeLevel | None = None
    start_date: str | None = None
    end_date: str | None = None


class DailyMenuUpdate(BaseModel):
    """日別献立更新リクエスト"""
    plan_id: int
    date: str  # YYYY-MM-DD
    menu: DailyMenuData


class MenuCopyRequest(BaseModel):
    """献立コピーリクエスト"""
    source_plan_id: int
    new_name: str
    start_date: str  # YYYY-MM-DD


class NutritionDailyRequest(BaseModel):
    """日別栄養分析リクエスト"""
    menu: DailyMenuData
    grade_level: SchoolGradeLevel = SchoolGradeLevel.ELEMENTARY_MID


class NutritionWeeklyRequest(BaseModel):
    """週間栄養分析リクエスト"""
    plan_id: int
    start_date: str  # YYYY-MM-DD (月曜日)


# --- Response Models ---

class MenuPlanResponse(BaseModel):
    """献立計画レスポンス"""
    id: int
    name: str
    grade_level: SchoolGradeLevel
    start_date: str
    end_date: str
    created_at: str


class DailyMenuResponse(BaseModel):
    """日別献立レスポンス"""
    plan_id: int
    date: str
    menu: DailyMenuData


class NutrientResult(BaseModel):
    """栄養素の分析結果"""
    key: str
    name: str
    unit: str
    actual: float
    standard: float
    ratio: float  # 達成率 (%)


class DailyNutritionResult(BaseModel):
    """日別栄養分析結果"""
    date: str
    total_cost: float
    nutrients: list[NutrientResult]
    achievement_rate: float  # 全体達成率 (%)


class WeeklyNutritionResult(BaseModel):
    """週間栄養分析結果"""
    start_date: str
    end_date: str
    daily_results: list[DailyNutritionResult]
    weekly_average: list[NutrientResult]
    total_cost: float
    average_achievement_rate: float
