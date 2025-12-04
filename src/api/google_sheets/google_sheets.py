import logging
import traceback
from typing import Optional

import time
import gspread
from google.oauth2.service_account import Credentials
from gspread import Worksheet
from vk_api import ApiError

from src.api.google_sheets.spread_sheet_manager import SpreadsheetManager
from src.config import config


class GoogleSheets:
    def __init__(self):
        """Подключение к Google Sheets"""
        try:
            self._scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            self._creds = Credentials.from_service_account_file(config.credentials_path, scopes=self._scope)
            self._client = gspread.authorize(self._creds)
            logging.info(f"Подключение к Google Sheets успешно")
            self._last_request_time = 0
            self._min_interval = 1.0

            self.manager = SpreadsheetManager()
        except Exception as e:
            logging.error(f"Произошла ошибка при подключении к Google Sheets: {e}\n{traceback.format_exc()}")

    def rate_limit(self) -> None:
        """Ограничение частоты запросов"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_interval:
            time.sleep(self._min_interval - time_since_last)
        self._last_request_time = time.time()

    def _get_sheet_with_retry(self, sheet_name=None, max_retries=3) -> Worksheet:
        """Получение листа с повторными попытками"""
        for attempt in range(max_retries):
            try:
                self.rate_limit()
                return self._client.open(config.spreadsheetname).worksheet(
                    sheet_name if sheet_name else config.default_sheet_name)
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
        return self._client.open(config.spreadsheetname).worksheet(sheet_name if sheet_name else config.default_sheet_name)