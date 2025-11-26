import logging
import traceback

from src.database.operations.admins import Admins
from src.services.general_functions import general_func
from src.services.handlers.posts.chat.controllers.posts import HandlerCommandsForPostsInChat
from src.services.handlers.chat_messages.commands import CommandsInChat


handler_commands_for_posts_in_chat = HandlerCommandsForPostsInChat()
class HandlerChatMessages(CommandsInChat):
    def handler_chat_message(self, msg, user_id, chat_id, event):
        forward_command = None

        for cmd in self.strict_commands:
            if msg.lower() == cmd.lower():
                forward_command = msg

        if not forward_command:
            for cmd in self.not_strict_commands:
                if cmd.lower() in msg.lower():
                    forward_command = cmd

        if not forward_command:
            handler_commands_for_posts_in_chat.handler_commands_for_posts(msg, user_id, chat_id, event)

        if forward_command:
            command = self.strict_commands.get(forward_command) or self.not_strict_commands.get(forward_command)

            if command["admin_only"] and str(user_id) not in str(Admins.get_admins_list()):
                general_func.sender(chat_id, f"У Вас нет доступа к этой команде")

            else:
                params = {}

                for param in command["params"]:
                    if param == "chat_id":
                        params["chat_id"] = chat_id
                    elif param == "msg":
                        params["msg"] = msg
                    elif param == "user_id":
                        params["user_id"] = user_id
                    elif param == "event":
                        params["event"] = event
                    elif param == "type1":
                        params["type"] = 1
                    elif param == "type2":
                        params["type"] = 2
                    elif param == "type3":
                        params["type"] = 3

                try:
                    command["handler"](**params)
                except Exception as e:
                    general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
                    logging.error(f"Ошибка при выполнении команды {forward_command}: {e}\n{traceback.format_exc()}")