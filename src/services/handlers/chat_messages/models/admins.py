from src.services.models.senders import Senders
from src.services.models.users import Users
from src.database.operations.admins import Admins


class AdminsModel:
    @staticmethod
    def add_admin(chat_id, msg, event):
        user_id = Users.give_user_id(chat_id, msg, event)

        if Admins.add_admin_to_db(user_id, chat_id) and user_id is not None:
            Senders.sender(chat_id, f"{Users.info_user(user_id)} добавлен(а) в список администраторов")

        elif user_id in Admins.get_admins_list() and user_id is not None:
            Senders.sender(chat_id, f"{Users.info_user(user_id)} уже есть в списке администраторов")

    @staticmethod
    def delete_admin(chat_id, msg, event):
        """Удаление администратора (/deladm)"""
        user_id = Users.give_user_id(chat_id, msg, event)

        if Admins.remove_admin_from_db(user_id, chat_id) and user_id is not None:
            Senders.sender(chat_id, f"{Users.info_user(user_id)} вынесен(а) из списка администраторов")

        elif user_id not in Admins.get_admins_list() and user_id is not None:
            Senders.sender(chat_id, f"{Users.info_user(user_id)} не найден(а) в списке администратора")

    @staticmethod
    def admins_list(chat_id):
        start_label = f"Список администрации:\n\n"
        for cell in Admins.get_admins_list():
            if cell is None:
                continue
            elif cell.strip():
                start_label += f"{Users.info_user(cell)}\n"

        Senders.sender(chat_id, f"{start_label}")
