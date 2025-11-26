from typing import Optional, List, Tuple

from src.database.db_connection import DataBase


class Posts(DataBase):
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

    def change_approved_posts(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика одобренных постов"""
        return self._change_counter('posts_info', 'approved_posts', status, chat_id)

    def change_posts_inspection(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика проверяемых постов"""
        return self._change_counter('posts_info', 'posts_inspection', status, chat_id)

    def change_posts(self, status: bool, chat_id: Optional[int] = None) -> bool:
        """Изменение счетчика постов"""
        return self._change_counter('posts_info', 'posts', status, chat_id)

