from typing import Optional, List, Tuple

from src.database.db_connection import DataBase


class PostAndUser(DataBase):
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
   