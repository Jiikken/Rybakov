from typing import Optional, List, Tuple

from src.database.db_connection import DataBase


class Admins(DataBase):
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
