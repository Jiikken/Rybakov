import time
from src.database.operations.posts import Posts
import logging
import traceback
from src.services.general_functions import general_func


class ThreadModel:
    @staticmethod
    def thread_info_posts():
        while True:
            current_time = time.localtime()
            if current_time.tm_hour == 21 and current_time.tm_min == 0:
                posts, approved_posts, posts_inspection = Posts.get_posts_info()
                try:
                    general_func.info_posts(posts, posts_inspection, approved_posts, 6)
                    Posts.reset_posts_info()
                except Exception as e:
                    general_func.sender(2, f"Ошибка при обращении к методу: {e}")
                    logging.error(
                        f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

            time.sleep(60)