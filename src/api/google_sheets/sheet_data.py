from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any

from gspread import Worksheet


@dataclass
class RedactorsData:
    """Структурированные данные о редакторах из таблиц"""
    ids: List[str] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    probation: List[str] = field(default_factory=list)
    posts_sent_for_review: List[str] = field(default_factory=list)
    all_posts: List[str] = field(default_factory=list)
    percent_approved_posts: List[str] = field(default_factory=list)
    statistics: List[str] = field(default_factory=list)
    approved_posts: List[str] = field(default_factory=list)
    loaded_at: datetime = field(default_factory=datetime.now)

@dataclass
class DaysData:
    date_reset_stats: Any = None
    days_reset_stats: List[str] = field(default_factory=list)
    days_since_reset_stats: int = 0
    loaded_at: datetime = field(default_factory=datetime.now)

@dataclass
class SheetsData:
    """Структурированные таблицы"""
    stats: Worksheet = field(default_factory=str)
    bot_sheet: Worksheet = field(default_factory=str)
    redactors_sheet: Worksheet = field(default_factory=str)
    stability: Worksheet = field(default_factory=str)
