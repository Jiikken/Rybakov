from src.services.models.senders import Senders
from src.services.models.users import users
from src.database.operations.admins import admins


class AdminsModel:
    @staticmethod
    def add_admin(chat_id: int, msg: str, event):
        """
        Добавление пользователя в базу данных администраторов (/addmin)

        :param chat_id: ID чата, где произошло событие
        :param msg: Сообщение события
        :param event: Событие
        """
        user_id = users.give_user_id(chat_id, msg, event)

        if admins.add_admin_to_db(user_id, chat_id) and user_id is not None:
            Senders.sender(chat_id, f"{users.info_user(user_id)} добавлен(а) в список администраторов")

        elif user_id in admins.get_admins_list() and user_id is not None:
            Senders.sender(chat_id, f"{users.info_user(user_id)} уже есть в списке администраторов")

    @staticmethod
    def delete_admin(chat_id: int, msg: str, event):
        """
        Удаление пользователя из базы данных администраторов (/deladm)

        :param chat_id: ID чата, где произошло событие
        :param msg: Сообщение события
        :param event: Событие
        """
        user_id = users.give_user_id(chat_id, msg, event)

        if admins.remove_admin_from_db(user_id, chat_id) and user_id is not None:
            Senders.sender(chat_id, f"{users.info_user(user_id)} вынесен(а) из списка администраторов")

        elif user_id not in admins.get_admins_list() and user_id is not None:
            Senders.sender(chat_id, f"{users.info_user(user_id)} не найден(а) в списке администратора")

    @staticmethod
    def admins_list(chat_id: int):
        """
        Отправляет список администраторов из базы данных

        :param chat_id: ID чата, где произошло событие
        """
        start_label = f"Список администрации:\n\n"
        for cell in admins.get_admins_list():
            if cell is None:
                continue
            elif cell.strip():
                start_label += f"{users.info_user(cell)}\n"

        Senders.sender(chat_id, f"{start_label}")
