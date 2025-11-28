import json
import time

from vk_api.bot_longpoll import VkBotEventType

from api.vk.vk import VkConnection
from src.database.operations.posts import Posts as PostsDataBase
from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.models.senders import Senders
from src.utils.keyboards import create_buttons


class CommandsModel:
    @staticmethod
    def enter_post(chat_id, user_id, event, content_chat = 5, admin_chat = 1):
        if PostsGoogleSheets.inactive_user(user_id, chat_id):
            Senders.sender(chat_id,
                   "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            message_id = event.message.get("conversation_message_id")
            midd = json.dumps(
                {"peer_id": 2000000000 + content_chat, "conversation_message_ids": message_id, "is_reply": False})
            Senders.sender(chat_id, f"Пост отправлен на рассмотрение под номером #{message_id}", midd)

            PostAndUser.add_post_to_user(message_id, user_id, chat_id)

            PostsGoogleSheets.summ_posts(user_id, chat_id)
            PostsDataBase.add_post_to_db(message_id, chat_id)

            PostsDataBase.change_posts_inspection(True, chat_id)
            PostsDataBase.change_posts(True, chat_id)

            Senders.sender(admin_chat, f"Внимание! Новая идея для поста #{message_id}", midd, keyboard=create_buttons(message_id))

    @staticmethod
    def wait_for_user_input(chat_id, message_id, timeout=60):
        """Для персонального ответа"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            for event in VkConnection.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat and event.chat_id == chat_id:
                        user_id = event.message.get("from_id")
                        if user_id == PostAndUser.get_admin_id_by_response_post(message_id):
                            user_response = event.object.message['text']
                            return user_response

        Senders.sender(chat_id, 'Время ожидания истекло')
        return None
