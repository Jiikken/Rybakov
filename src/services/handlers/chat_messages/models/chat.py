import logging
import traceback

from vk_api import ApiError

from api.vk.vk import VkConnection
from src.services.general_functions import general_func
from src.database.operations.admins import Admins


class ChatModel:
    @staticmethod
    def cid(chat_id):
        """Информация о ID текущей беседы"""
        general_func.sender(chat_id, f"ID текущей конференции: {chat_id}")

    @staticmethod
    def kick_user(chat_id, msg, event):
        """Кик пользователя"""
        user_id = general_func.give_user_id(chat_id, msg, event)

        if user_id in Admins.get_admins_list():
            general_func.sender(chat_id, "Этот пользователь является администратором")

        elif user_id is not None:
            try:
                VkConnection.vk_api.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
            except ApiError as e:
                if e.code == 15:
                    general_func.sender(chat_id, f"Пользователь является администратором в беседе")
                if e.code == 935:
                    general_func.sender(chat_id, f"Пользователь не найден в беседе")
            except Exception as e:
                general_func.sender(chat_id, f"Данного пользователя нельзя исключить")
                logging.warning(f"Ошибка при исключении пользователя: {e}\n{traceback.format_exc()}")
                