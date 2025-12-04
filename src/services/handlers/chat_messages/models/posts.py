from src.database.operations.posts import posts_data_base
from src.services.models.senders import Senders
from src.services.models.posts import info_about_posts_in_chat
from src.api.google_sheets.posts import posts_google_sheets


class PostsModel:
    @staticmethod
    def no_check_posts(chat_id: int):
        """
        Список непроверенных постов (/posts)

        :param chat_id: ID чата, где произошло событие
        """
        if posts_data_base.get_no_check_posts_list():
            ip = ""
            for i in posts_data_base.get_no_check_posts_list():
                ip += f" #{i}"
            Senders.sender(chat_id, f"Непроверенные посты:{ip}")
        else:
            Senders.sender(chat_id, "Непроверенных постов нет")

    @staticmethod
    def info_posts_per_day(chat_id: int):
        """
        Информация о постах отправленных на проверку за один день (/fo)

        :param chat_id: ID чата, где произошло событие
        """
        posts, approved_posts, posts_inspection = posts_data_base.get_posts_info()
        info_about_posts_in_chat.info_posts(posts, approved_posts, posts_inspection, chat_id)

    @staticmethod
    def info_posts_per_month(chat_id: int):
        """
        Информация о выложенных постах за месяц (/infopost)

        :param chat_id: ID чата, где произошло событие
        """
        posts_google_sheets.info_posts_per_month(chat_id)