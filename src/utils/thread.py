import logging
import time
import traceback

from src.database.operations.posts import posts_data_base
from src.services.models.posts import info_about_posts_in_chat
from src.services.models.senders import Senders


class ThreadModel:
    @staticmethod
    def thread_info_posts():
        """Метод для ежедневного оповещения редакторов о статистике постов за день"""
        while True:
            current_time = time.localtime()
            if current_time.tm_hour == 21 and current_time.tm_min == 0:
                posts, approved_posts, posts_inspection = posts_data_base.get_posts_info()
                try:
                    info_about_posts_in_chat.info_posts(posts, posts_inspection, approved_posts, 6)
                    posts_data_base.reset_posts_info()
                except Exception as e:
                    Senders.sender(2, f"Ошибка при обращении к методу: {e}")
                    logging.error(
                        f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

            time.sleep(60)