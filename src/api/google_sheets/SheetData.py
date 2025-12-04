from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class SheetData:
    """Структурированные данные из таблицы"""
    ids: List[str] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    probation: List[str] = field(default_factory=list)
    posts_sent_for_review: List[str] = field(default_factory=list)
    all_posts: List[str] = field(default_factory=list)
    percent_approved_posts: List[str] = field(default_factory=list)
    statistics: List[str] = field(default_factory=list)
    approved_posts: List[str] = field(default_factory=list)
    day_reset_stats: Any = None
    days_reset_stats: List[str] = field(default_factory=list)
    days_since_restart: int = 0
    loaded_at: datetime = field(default_factory=datetime.now)
