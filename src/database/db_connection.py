import traceback
import logging

from contextlib import contextmanager
from src.config import config

import sqlite3

from src.services.general_functions import general_func


class DataBase:
    @staticmethod
    @contextmanager
    def get_db_connection():
        """Контекстный менеджер для подключения к БД с обработкой ошибок"""
        conn = None
        try:
            conn = sqlite3.connect(
                config.db_path,
                timeout=30.0,  # Увеличенный таймаут для избежания блокировок
                check_same_thread=False  # Для многопоточного использования
            )
            conn.execute("PRAGMA journal_mode=WAL")  # Режим записи в журнал
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Ошибка подключения к БД: {e}\n{traceback.format_exc()}")
            raise
        finally:
            if conn:
                conn.close()

    def _execute_db_operation(self, operation, *args, default_return=None, chat_id=None):
        """Обертка для выполнения операций с БД"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                result = operation(cursor, *args)
                conn.commit()
                return result
        except sqlite3.IntegrityError:
            return default_return
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            if chat_id:
                general_func.sender(chat_id, "Произошла ошибка при обращении к базе данных")
                logging.error(f"Произошла ошибка при обращении к базе данных: {e}\n{traceback.format_exc()}")
            return default_return