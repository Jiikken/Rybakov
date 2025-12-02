from src.database.operations.posts import posts_data_base
from src.api.google_sheets.posts import posts_google_sheets
from src.database.operations.post_and_user import post_and_user
from src.services.models.senders import Senders
from src.utils.keyboards import Keyboards


class CommandsForPostsInLS:
    @staticmethod
    def enter_post_ls(user_id: int, event, admin_chat: int = 1):
        """Отправка поста на проверку в ЛС"""
        if posts_google_sheets.inactive_user(user_id):
            Senders.sender_in_ls(user_id,
                         "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            user_id = event.message.get("from_id")
            message_id = event.message.get("id")

            Senders.sender_in_ls(user_id, f"Пост отправлен на рассмотрение под номером #{message_id}", message_id)

            post_and_user.add_post_to_user(message_id, user_id)

            posts_google_sheets.summ_posts(user_id)
            posts_data_base.add_post_to_db(message_id)

            posts_data_base.change_posts_inspection(True)
            posts_data_base.change_posts(True)

            Senders.resend_in_ls(admin_chat, f"Внимание! Новая идея для поста #{message_id}", message_id,
                         keyboard=Keyboards.create_buttons_ls(message_id))