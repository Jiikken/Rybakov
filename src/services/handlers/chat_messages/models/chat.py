import logging
import traceback

from vk_api import ApiError

from src.api.vk.vk import VkConnection
from src.services.models.users import users
from src.services.models.senders import Senders
from src.database.operations.admins import admins


class ChatModel:
    @staticmethod
    def cid(chat_id: int):
        """
        Информация о ID текущего чата (/cid)

        :param chat_id: ID чата, где произошло событие
        """
        Senders.sender(chat_id, f"ID текущей конференции: {chat_id}")

    @staticmethod
    def kick_user(chat_id: int, msg: str, event):
        """
        Исключение пользователя из чата, где была прописана команда (/kick)

        :param chat_id: ID чата, где произошло событие
        :param msg: Сообщение события
        :param event: Событие
        """
        user_id = users.give_user_id(chat_id, msg, event)

        if user_id in admins.get_admins_list():
            Senders.sender(chat_id, "Этот пользователь является администратором")

        elif user_id is not None:
            try:
                VkConnection.vk_api.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
            except ApiError as e:
                if e.code == 15:
                    Senders.sender(chat_id, f"Пользователь является администратором в беседе")
                if e.code == 935:
                    Senders.sender(chat_id, f"Пользователь не найден в беседе")
            except Exception as e:
                Senders.sender(chat_id, f"Данного пользователя нельзя исключить")
                logging.warning(f"Ошибка при исключении пользователя: {e}\n{traceback.format_exc()}")
                