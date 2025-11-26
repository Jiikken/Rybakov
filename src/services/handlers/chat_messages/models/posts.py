from src.database.operations.posts import Posts
from src.services.general_functions import general_func
from src.api.google_sheets.statistics import Statistics


class PostsModel:
    @staticmethod
    def no_check_posts(chat_id):
        """Непроверенные посты (/posts)"""
        if Posts.get_no_check_posts_list():
            ip = ""
            for i in Posts.get_no_check_posts_list():
                ip += f" #{i}"
            general_func.sender(chat_id, f"Непроверенные посты:{ip}")
        else:
            general_func.sender(chat_id, "Непроверенных постов нет")

    @staticmethod
    def info_posts_per_day(chat_id):
        posts, approved_posts, posts_inspection = Posts.get_posts_info()
        general_func.info_posts(posts, approved_posts, posts_inspection, chat_id)

    @staticmethod
    def info_posts_per_month(chat_id):
        Statistics.info_posts_per_month(chat_id)