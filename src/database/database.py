import traceback
from contextlib import contextmanager
from src.config import config
from src.utils.logs import logging
import sqlite3
from typing import Optional, List, Tuple
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

    # Функции для работы с администраторами
    def get_admins_list(self) -> List[str]:
        """Получение списка всех администраторов"""
        def op(cursor):
            cursor.execute('SELECT user_id FROM admins')
            return [row[0] for row in cursor.fetchall()]
        return self._execute_db_operation(op) or []

    def add_admin_to_db(self, user_id: str, chat_id: Optional[int] = None) -> bool:
        """Добавление администратора"""
        def op(cursor, uid):
            cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (uid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, user_id, default_return=False, chat_id=chat_id)

    def remove_admin_from_db(self, user_id: str, chat_id: Optional[int] = None) -> bool:
        """Удаление администратора"""
        def op(cursor, uid):
            cursor.execute('DELETE FROM admins WHERE user_id = ?', (uid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, user_id, default_return=False, chat_id=chat_id)

    # Функции для работы с постами
    def get_no_check_posts_list(self) -> List[str]:
        """Получение списка непроверенных постов"""
        def op(cursor):
            cursor.execute('SELECT message_id FROM no_check_posts')
            return [row[0] for row in cursor.fetchall()]
        return self._execute_db_operation(op) or []

    def add_post_to_db(self, message_id: int, chat_id: Optional[int] = None) -> bool:
        """Добавление поста в БД"""
        def op(cursor, mid):
            cursor.execute('INSERT OR IGNORE INTO no_check_posts (message_id) VALUES (?)', (mid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, default_return=False, chat_id=chat_id)

    def remove_post_from_db(self, message_id: int, chat_id: Optional[int] = None) -> bool:
        """Удаление поста из БД"""
        def op(cursor, mid):
            cursor.execute('DELETE FROM no_check_posts WHERE message_id = ?', (mid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, default_return=False, chat_id=chat_id)

    # Функции для работы со связями постов и пользователей
    def add_post_to_user(self, message_id: int, user_id: int, chat_id: Optional[int] = None) -> bool:
        """Добавление связи пост-пользователь"""
        def op(cursor, mid, uid):
            cursor.execute('INSERT OR IGNORE INTO post_to_user (message_id, user_id) VALUES (?, ?)', (mid, uid))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, user_id, default_return=False, chat_id=chat_id)

    def remove_post_to_user(self, message_id: int, chat_id: Optional[int] = None) -> bool:
        """Удаление связи пост-пользователь"""
        def op(cursor, mid):
            cursor.execute('DELETE FROM post_to_user WHERE message_id = ?', (mid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, default_return=False, chat_id=chat_id)

    def get_user_by_post(self, message_id: int, chat_id: Optional[int] = None) -> Optional[int]:
        """Получение пользователя по ID поста"""
        def op(cursor, mid):
            cursor.execute('SELECT user_id FROM post_to_user WHERE message_id = ?', (mid,))
            result = cursor.fetchone()
            return result[0] if result else None
        return self._execute_db_operation(op, message_id, default_return=None, chat_id=chat_id)

    def add_personal_response_to_post(self, message_id: int, user_id: int, chat_id: Optional[int] = None) -> bool:
        """Добавление поста в БД"""
        def op(cursor, mid, uid):
            cursor.execute('INSERT OR IGNORE INTO personal_response_to_post (message_id, user_id) VALUES (?, ?)', (mid, uid))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, user_id, default_return=False, chat_id=chat_id)

    def remove_personal_response_to_post(self, message_id: int, chat_id: Optional[int] = None) -> bool:
        """Добавление поста в БД"""
        def op(cursor, mid):
            cursor.execute('DELETE FROM personal_response_to_post WHERE message_id = ?', (mid,))
            return cursor.rowcount > 0
        return self._execute_db_operation(op, message_id, default_return=False, chat_id=chat_id)

    def get_admin_id_by_response_post(self, message_id: int, chat_id: Optional[int] = None):
        def op(cursor, mid):
            cursor.execute('SELECT user_id FROM personal_response_to_post WHERE message_id = ?', (mid,))
            result = cursor.fetchone()
            return result[0] if result else None
        return self._execute_db_operation(op, message_id, default_return=None, chat_id=chat_id)

    # Функции для работы со статистикой
    def get_posts_info(self) -> Tuple[int, int, int]:
        """Получение информации о постах"""
        def op(cursor):
            cursor.execute('SELECT posts, approved_posts, posts_inspection FROM posts_info WHERE id = 1')
            return cursor.fetchone()
        return self._execute_db_operation(op) or (0, 0, 0)

    def reset_posts_info(self, chat_id: Optional[int] = None) -> bool:
        """Сброс информации о постах"""
        def op(cursor):
            cursor.execute('UPDATE posts_info SET posts = 0, approved_posts = 0 WHERE id = 1')
            return cursor.rowcount > 0
        return self._execute_db_operation(op, default_return=False, chat_id=chat_id)

    # Функции для изменения счетчиков
    def _change_counter(self, table: str, field: str, status: bool, chat_id: Optional[int] = None) -> bool:
        """Общая функция для изменения счетчиков"""
        def op(cursor):
            operator = '+' if status else '-'
            cursor.execute(f'UPDATE {table} SET {field} = {field} {operator} 1 WHERE id = 1')
            return cursor.rowcount > 0
        return self._execute_db_operation(op, default_return=False, chat_id=chat_id)

    def change_approved_posts(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика одобренных постов"""
        return self._change_counter('posts_info', 'approved_posts', status, chat_id)

    def change_posts_inspection(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика проверяемых постов"""
        return self._change_counter('posts_info', 'posts_inspection', status, chat_id)

    def change_posts(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика постов"""
        return self._change_counter('posts_info', 'posts', status, chat_id)

database = DataBase()
