import time

from src.api.google_sheets.google_sheets import GoogleSheets
from src.api.google_sheets.sheet_data import ColumnsData, SheetsData


class SpreadsheetManager(GoogleSheets):
    def __init__(self):
        super().__init__()
        self._sheets_cache = None
        self._columns_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 3600

    @property
    def sheets(self) -> SheetsData:
        """Кэшированные таблицы"""
        if self._should_refresh_cache():
            self._sheets_cache = self._load_sheets()
            self._cache_timestamp = time.time()
        return self._sheets_cache

    @property
    def columns(self) -> ColumnsData:
        """Кэшированные колонки"""
        if self._columns_cache is None or self._should_refresh_cache():
            self._columns_cache = self._load_columns()
        return self._columns_cache

    def _should_refresh_cache(self) -> bool:
        """Проверяем, нужно ли обновить кэш"""
        if self._sheets_cache is None:
            return True
        if self._cache_timestamp is None:
            return True
        # Проверяем TTL (Time To Live)
        return (time.time() - self._cache_timestamp) > self._cache_ttl

    def _load_sheets(self) -> SheetsData:
        """Загрузка таблиц"""
        stats_sheet = self._get_sheet("Статистика")
        bot_sheet = self._get_sheet("Информация для бота")
        redactors_work_sheet = self._get_sheet("Работа")
        stability = self._get_sheet("Стабильность")

        return SheetsData(
            stats=stats_sheet,
            bot_sheet=bot_sheet,
            redactors_sheet=redactors_work_sheet,
            stability=stability
        )

    def _load_columns(self) -> ColumnsData:
        """Извлечение данных в структурированном виде"""
        sheets = self.sheets  # Используем property, чтобы получить кэшированные данные

        return ColumnsData(
            ids=sheets.bot_sheet.col_values(1)[1:],
            names=sheets.stats.col_values(2)[1:],
            probation=sheets.stats.col_values(11)[1:],
            all_posts=sheets.stats.col_values(6)[1:],
            percent_approved_posts=sheets.stats.col_values(9)[1:],
            statistics=sheets.stats.col_values(8)[1:],
            posts_sent_for_review=sheets.bot_sheet.col_values(2)[1:],
            day_reset_stats=sheets.bot_sheet.acell("B32"),
            days_reset_stats=sheets.stability.row_values(1),
            approved_posts=sheets.bot_sheet.col_values(3)[1:],
            days_since_restart=int(sheets.bot_sheet.acell("B32").value)
        )

    def invalidate_cache(self):
        """Принудительно сбросить кэш"""
        self._sheets_cache = None
        self._columns_cache = None
        self._cache_timestamp = None
