import os
import traceback

from dotenv import load_dotenv

from src.utils.logs import logging


class Cfg:
    def __init__(self):
        """Основные переменные для работы с ботом"""
        try:
            self.env_path = os.path.join(os.path.dirname(__file__), "..", "secrets", ".env")
            load_dotenv(dotenv_path=self.env_path)
            self.vk_token = os.getenv("VK_TOKEN")
            self.group_id = 228911906
            self.db_path = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")
            self.credentials_path = os.path.join(os.path.dirname(__file__), "..", "secrets", "credentials.json")
            self.spreadsheetname = "Корпорация  — AMAZING (БОТ)"
            self.default_sheet_name = "БОТ Корпорация"

            if self.vk_token is not None and self.db_path is not None and self.credentials_path is not None:
                logging.info(f"Основные переменные успешно инициализированы")
            else:
                logging.warning(f"Одна или несколько основных переменных не были авторизованы")
        except Exception as e:
            logging.critical(f"Произошла ошибка при инициализации основных переменных: {e}\n{traceback.format_exc()}")

config = Cfg()