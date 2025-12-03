import logging
import traceback
from typing import Optional

import time
import gspread
from google.oauth2.service_account import Credentials
from gspread import Worksheet

from src.config import config


class GoogleSheets:
    def __init__(self):
        """Подключение к Google Sheets"""
        try:
            self.scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            self.creds = Credentials.from_service_account_file(config.credentials_path, scopes=self.scope)
            self.client = gspread.authorize(self.creds)
            logging.info(f"Подключение к Google Sheets успешно")
            self.last_request_time = 0
            self.min_interval = 1.0
        except Exception as e:
            logging.error(f"Произошла ошибка при подключении к Google Sheets: {e}\n{traceback.format_exc()}")

    def rate_limit(self) -> None:
        """Ограничение частоты запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

    def _get_sheet(self, sheet_name: Optional[str] = None) -> Worksheet:
        """Получение таблицы по названию"""
        return self.client.open(config.spreadsheetname).worksheet(sheet_name if sheet_name else config.default_sheet_name)

    def get_sheets(self) -> dict:
        """
        keys in dictionary:

            - "stats"
            - "bot_sheet"
            - "redactors_sheet"
            - "stability"

        :return: dictionary
        """
        stats_sheet = self._get_sheet("Статистика")
        bot_sheet = self._get_sheet("Информация для бота")
        redactors_work_sheet = self._get_sheet("Работа")
        stability = self._get_sheet("Стабильность")

        sheets = {
            "stats": stats_sheet,
            "bot_sheet": bot_sheet,
            "redactors_sheet": redactors_work_sheet,
            "stability": stability
        }

        return sheets

    def get_columns(self) -> dict:
        """
        keys in dictionary:

            - "ids"
            - "names"
            - "probation"
            - "posts_sent_for_review"
            - "all_posts"
            - "percent_approved_posts"
            - "statistics"
            - "day_reset_stats"
            - "days_reset_stats"
            - "approved_posts"

        :return: dictionary
        """
        sheets = self.get_sheets()

        redactors_names = sheets["stats"].col_values(2)[1:]  # Имена ВК
        probation = sheets["stats"].col_values(11)[1:]  # Должность
        all_posts = sheets["stats"].col_values(6)[1:]  # Все посты
        percent_approved_posts = sheets["stats"].col_values(9)[1:]  # Процент одобрения из столбца K
        redactors_statistics = sheets["stats"].col_values(8)[1:]  # Статистика
        posts_sent_for_review = sheets["bot_sheet"].col_values(2)[1:]  # Посты отправленные на проверку
        redactors_ids = sheets["bot_sheet"].col_values(1)[1:]  # IDs редакторов
        day_reset_stats = sheets["bot_sheet"].acell("B32")
        days_reset_stats = sheets["stability"].row_values(1)
        approved_posts = sheets["bot_sheet"].col_values(3)[1:]

        columns = {
            "ids": redactors_ids,
            "names": redactors_names,
            "probation": probation,
            "posts_sent_for_review": posts_sent_for_review,
            "all_posts": all_posts,
            "percent_approved_posts": percent_approved_posts,
            "statistics": redactors_statistics,
            "day_reset_stats": day_reset_stats,
            "days_reset_stats": days_reset_stats,
            "approved_posts": approved_posts
        }

        return columns