import logging
import traceback
from typing import Optional

from vk_api import ApiError

from src.api.vk.vk import VkConnection


class Senders:
    @staticmethod
    def sender(chat_id: int, text: str, mid: Optional[str] = None, keyboard: Optional[str] = None):
        """
        Метод отправки сообщений в беседы

        :param chat_id: ID чата для отправки (обязательный параметр)
        :param text: Текст отправляемого сообщения (обязательный параметр)
        :param mid: Пересылаемое сообщение
        :param keyboard: Клавиатура для сообщения
        """
        try:
            VkConnection.vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0, 'forward': mid, 'keyboard': keyboard})
        except ApiError as a:
            if a.code == 100:
                Senders.sender(chat_id, f"Перешлите это сообщение Кириллу")
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(sender): {e}\n{traceback.format_exc()}")

    @staticmethod
    def sender_in_ls(user_id: int, text: str, mid: Optional[str] = None, keyboard: Optional[str] = None, attachment = None):
        """
        Метод отправки сообщений в ЛС

        :param user_id: ID пользователя, которому нужно отправить сообщение (обязательный параметр)
        :param text: Текст отправляемого сообщения (обязательный параметр)
        :param mid: Пересылаемое сообщение
        :param keyboard: Клавиатура для сообщения
        :param attachment: Вложение в сообщение
        """
        try:
            VkConnection.vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': 0, 'attachment': attachment, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            Senders.sender(user_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(sender_in_ls): {e}\n{traceback.format_exc()}")

    @staticmethod
    def resend_from_ls(chat_id: int, text: str, mid: Optional[str], keyboard = None):
        """
        Пересылка сообщения из ЛС в чаты

        :param chat_id: ID чата, куда пересылать сообщение (обязательный параметр)
        :param text: Текст сообщения (обязательный параметр)
        :param mid: Пересылаемое сообщение (обязательный параметр)
        :param keyboard: Клавиатура для сообщения
        """
        try:
            VkConnection.vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(resend_in_ls): {e}\n{traceback.format_exc()}")