import json

from src.api.google_sheets.posts import posts_google_sheets
from src.database.operations.post_and_user import post_and_user
from src.database.operations.posts import posts_data_base
from src.services.models.senders import Senders
from src.utils.keyboards import Keyboards

class CommandsForPostsInChat:
    @staticmethod
    def enter_post_chat(chat_id: int, user_id: int, event, content_chat: int = 5, admin_chat: int = 1):
        """
        Метод для отправки постов

        :param chat_id: ID чата, куда было прислано сообщение
        :param user_id: ID пользователя, от кого поступило сообщение
        :param event: Событие
        :param content_chat: ID чата для контента, по умолчанию 5
        :param admin_chat: ID чата для проверки контента, по умолчанию 1
        """
        if posts_google_sheets.inactive_user(user_id, chat_id):
            Senders.sender(chat_id,
                   "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            message_id = event.message.get("conversation_message_id")
            midd = json.dumps(
                {"peer_id": 2000000000 + content_chat, "conversation_message_ids": message_id, "is_reply": False})
            Senders.sender(chat_id, f"Пост отправлен на рассмотрение под номером #{message_id}", midd)

            post_and_user.add_post_to_user(message_id, user_id, chat_id)

            posts_google_sheets.summ_posts(user_id, chat_id)
            posts_data_base.add_post_to_db(message_id, chat_id)

            posts_data_base.change_posts_inspection(True, chat_id)
            posts_data_base.change_posts(True, chat_id)

            Senders.sender(admin_chat, f"Внимание! Новая идея для поста #{message_id}", midd, keyboard=Keyboards.create_buttons(message_id))
