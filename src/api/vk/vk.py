import logging
import traceback

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from src.config import config


class MyLongPoll(VkBotLongPoll):
    """Прослушка событий в чатах"""
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                logging.critical(f"Ошибка в прослушивании событий: {e}\n{traceback.format_exc()}")

class VkConnection:
    """Подключение к vk_api"""
    def __init__(self):
        try:
            self.vk_session = vk_api.VkApi(token=config.vk_token)
            self.vk_api = self.vk_session.get_api()
            self.longpoll = MyLongPoll(self.vk_session, config.group_id)
            logging.info(f"Подключение к vk_api успешно")
        except Exception as e:
            logging.critical(f"Ошибка при авторизации vk_api: {e}\n{traceback.format_exc()}")

vk_connect = VkConnection()