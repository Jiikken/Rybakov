import traceback

from src.services.handlers.posts.commands import CommandsPosts
from src.services.models.senders import Senders
from src.utils.logs import logging


class HandlerCommandsForPostsInLS(CommandsPosts):
    def handler_commands_for_posts(self, msg, user_id, event):
        forward_message = None

        for cmd in self.commands_for_posts_in_ls:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        if forward_message:
            command = self.commands_for_posts_in_ls.get(forward_message)

            try:
                command["handler"](user_id, event)
            except Exception as e:
                Senders.sender_in_ls(user_id, f"Произошла ошибка при обращении к методу")
                logging.error(f"Ошибка при выполнении команды {forward_message}: {e}\n{traceback.format_exc()}")

handler_commands_for_posts_in_ls = HandlerCommandsForPostsInLS()