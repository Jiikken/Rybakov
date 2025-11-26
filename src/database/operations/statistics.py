from typing import Optional, List, Tuple

from src.database.db_connection import DataBase


class Statistics(DataBase):
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

    