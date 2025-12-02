import logging
import traceback
from typing import Optional

import time
import gspread
from google.oauth2.service_account import Credentials
from gspread import Worksheet
from vk_api import ApiError

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
            self.min_interval = 1.0  # Минимальная задержка между запросами в секундах
        except Exception as e:
            logging.error(f"Произошла ошибка при подключении к Google Sheets: {e}\n{traceback.format_exc()}")

    def _rate_limit(self) -> None:
        """Ограничение частоты запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

    def _get_sheet_with_retry(self, sheet_name=None, max_retries=3) -> Worksheet:
        """Получение листа с повторными попытками"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                return self.client.open(config.spreadsheetname).worksheet(sheet_name if sheet_name else config.default_sheet_name)
            except ApiError as e:
                if '429' in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1  # Экспоненциальная backoff
                    logging.warning(f"Rate limit exceeded, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

    def _get_sheet(self, sheet_name: Optional[str] = None) -> Worksheet:
        """Получение таблицы по названию"""
        return self.client.open(config.spreadsheetname).worksheet(sheet_name if sheet_name else config.default_sheet_name)

    