import json
import logging
import traceback
from typing import Optional

from vk_api import ApiError

from src.api.vk.vk import VkConnection


class Senders:
    @staticmethod
    def sender(chat_id: int, text: str, mid: Optional[str] = None, keyboard: Optional[str] = None):
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
        try:
            VkConnection.vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': 0, 'attachment': attachment, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            Senders.sender(user_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(sender_in_ls): {e}\n{traceback.format_exc()}")

    @staticmethod
    def resend_in_ls(chat_id: int, text: str, mid: Optional[str], keyboard = None):
        """resend message from ls"""
        try:
            VkConnection.vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(resend_in_ls): {e}\n{traceback.format_exc()}")

    @staticmethod
    def get_midd(msg, chat_id, message_from_chat = 5):
        """Получение пересылаемого JSON для пересылки сообщения"""
        try:
            midd = json.dumps(
                {'peer_id': 2000000000 + message_from_chat, 'conversation_message_ids': Senders.get_post_id_from_message(chat_id, msg),
                 'is_reply': False})
        except Exception as e:
            logging.error(f"Произошла ошибка при нахождения midd: {e}\n{traceback.format_exc()}")
            midd = None

        return midd