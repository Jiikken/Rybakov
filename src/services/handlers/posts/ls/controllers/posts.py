import traceback

from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.general_functions import general_func
from src.utils.keyboards import cheburek
from src.utils.logs import logging
from src.services.handlers.posts.commands import CommandsPosts


class HandlerCommandsForPostsInLS(CommandsPosts):
    def handler_ls_messages(self, msg, user_id, event):
        forward_message = None

        for cmd in self.commands_for_posts_in_ls:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        if forward_message:
            command = self.commands_for_posts_in_ls.get(forward_message)

            try:
                command["handler"](user_id, event)
            except Exception as e:
                general_func.sender_in_ls(user_id, f"Произошла ошибка при обращении к методу")
                logging.error(f"Ошибка при выполнении команды {forward_message}: {e}\n{traceback.format_exc()}")
        elif msg.lower() == "хочу":
            self.send_cheburek(user_id)
        elif msg.lower() == "пельмень":
            self.send_dikiy_ogyrec(user_id)
        else:
            general_func.sender_in_ls(user_id, f"Здравствуйте, {general_func.info_user(user_id)}\n\nХотите чебурек?", keyboard=cheburek())
