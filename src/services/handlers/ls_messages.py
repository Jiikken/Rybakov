import traceback

from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.posts import Posts as PostsDataBase
from src.database.operations.post_and_user import PostAndUser as PostsAndUser
from src.services.general_functions import general_func
from src.utils.keyboards import create_buttons_ls
from src.utils.logs import logging
from src.services.handlers.posts import HandlerCommandsForPostsInLS


handler_commands_for_posts_in_ls = HandlerCommandsForPostsInLS()
class HandlerLSMessages:
    def __init__(self):
        self.commands_for_posts = {
            "#шишки": {
                "handler": self._handle_enter_post_in_ls
            }
        }

    def handler_ls_messages(self, msg, user_id, chat_id, event):
        forward_message = None

        for cmd in self.commands_for_posts:
            if cmd.lower() in msg.lower():
                forward_message = msg.lower()

        if forward_message:
            command = self.commands_for_posts.get(forward_message)

            try:
                command["handler"](user_id, event)
            except Exception as e:
                general_func.sender_in_ls(chat_id, f"Произошла ошибка при обращении к методу")
                logging.error(f"Ошибка при выполнении команды {forward_message}: {e}\n{traceback.format_exc()}")

        else:
            handler_commands_for_posts_in_ls.handler_ls_messages(msg, user_id, event)

    @staticmethod
    def _handle_enter_post_in_ls(user_id, event, admin_chat = 1):
        """Отправка поста на проверку в ЛС"""
        if PostsGoogleSheets.Posts.inactive_user(user_id):
            general_func.sender_in_ls(user_id,
                         "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            user_id = event.message.get("from_id")
            message_id = event.message.get("id")

            general_func.sender_in_ls(user_id, f"Пост отправлен на рассмотрение под номером #{message_id}", message_id)

            PostsAndUser.add_post_to_user(message_id, user_id)

            PostsGoogleSheets.summ_posts(user_id)
            PostsDataBase.add_post_to_db(message_id)

            general_func.resend_in_ls(admin_chat, f"Внимание! Новая идея для поста #{message_id}", message_id,
                         keyboard=create_buttons_ls(message_id))