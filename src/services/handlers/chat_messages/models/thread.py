import time
import logging
import traceback

from src.database.operations.posts import Posts as PostsDataBase
from src.services.models.senders import Senders
from src.services.models.posts import Posts


class ThreadModel:
    @staticmethod
    def thread_info_posts():
        while True:
            current_time = time.localtime()
            if current_time.tm_hour == 21 and current_time.tm_min == 0:
                posts, approved_posts, posts_inspection = PostsDataBase.get_posts_info()
                try:
                    Posts.info_posts(posts, posts_inspection, approved_posts, 6)
                    PostsDataBase.reset_posts_info()
                except Exception as e:
                    Senders.sender(2, f"Ошибка при обращении к методу: {e}")
                    logging.error(
                        f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

            time.sleep(60)