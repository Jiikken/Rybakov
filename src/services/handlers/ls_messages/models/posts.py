from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.posts import Posts as PostsDataBase
from src.database.operations.post_and_user import PostAndUser as PostsAndUser
from src.utils.keyboards import create_buttons_ls
from src.services.models.senders import Senders


class PostsModel:
    @staticmethod
    def handle_enter_post_in_ls(user_id, event, admin_chat = 1):
        """Отправка поста на проверку в ЛС"""
        if PostsGoogleSheets.Posts.inactive_user(user_id):
            Senders.sender_in_ls(user_id,
                         "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            user_id = event.message.get("from_id")
            message_id = event.message.get("id")

            Senders.sender_in_ls(user_id, f"Пост отправлен на рассмотрение под номером #{message_id}", message_id)

            PostsAndUser.add_post_to_user(message_id, user_id)

            PostsGoogleSheets.summ_posts(user_id)
            PostsDataBase.add_post_to_db(message_id)

            Senders.resend_in_ls(admin_chat, f"Внимание! Новая идея для поста #{message_id}", message_id,
                         keyboard=create_buttons_ls(message_id))