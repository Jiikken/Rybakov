import logging
import traceback

from src.database.operations.admins import admins
from src.services.models.senders import Senders
from src.services.handlers.posts.chat.controllers.handler_posts_chat import HandlerCommandsForPostsInChat
from src.services.handlers.chat_messages.commands import CommandsInChat


handler_commands_for_posts_in_chat = HandlerCommandsForPostsInChat()
class HandlerChatMessages(CommandsInChat):
    def handler_chat_message(self, msg: str, user_id: int, chat_id: int, event):
        forward_command = self._find_command(msg, user_id, chat_id, event)

        if forward_command:
            command = self.strict_commands.get(forward_command) or self.not_strict_commands.get(forward_command)

            if command["admin_only"] and str(user_id) not in str(admins.get_admins_list()):
                Senders.sender(chat_id, f"У Вас нет доступа к этой команде")

            else:
                params = self._fill_dictionary(command, chat_id, msg, user_id, event)
                try:
                    command["handler"](**params)
                except Exception as e:
                    Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
                    logging.error(f"Ошибка при выполнении команды {forward_command}: {e}\n{traceback.format_exc()}")

    def _find_command(self, msg: str, user_id: int, chat_id: int, event) -> str:
        forward_command = None

        for cmd in self.strict_commands:
            if msg.lower() == cmd.lower():
                forward_command = msg
                break

        if forward_command is None:
            for _cmd in self.not_strict_commands:
                if _cmd.lower() in msg.lower():
                    forward_command = _cmd
                    break

            handler_commands_for_posts_in_chat.handler_commands_for_posts(msg, user_id, chat_id, event)

        return forward_command

    @staticmethod
    def _fill_dictionary(command: dict, chat_id: int, msg: str, user_id: int, event) -> dict:
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

        return params

handler_chat_messages = HandlerChatMessages()
