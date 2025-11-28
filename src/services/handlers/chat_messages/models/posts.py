from src.database.operations.posts import Posts as PostsDataBase
from src.services.models.senders import Senders
from src.services.models.posts import Posts 
from src.api.google_sheets.statistics import Statistics


class PostsModel:
    @staticmethod
    def no_check_posts(chat_id):
        """Непроверенные посты (/posts)"""
        if Posts.get_no_check_posts_list():
            ip = ""
            for i in PostsDataBase.get_no_check_posts_list():
                ip += f" #{i}"
            Senders.sender(chat_id, f"Непроверенные посты:{ip}")
        else:
            Senders.sender(chat_id, "Непроверенных постов нет")

    @staticmethod
    def info_posts_per_day(chat_id):
        posts, approved_posts, posts_inspection = PostsDataBase.get_posts_info()
        Posts.info_posts(posts, approved_posts, posts_inspection, chat_id)

    @staticmethod
    def info_posts_per_month(chat_id):
        Statistics.info_posts_per_month(chat_id)