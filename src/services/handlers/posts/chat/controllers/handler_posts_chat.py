import traceback

from src.services.handlers.posts.chat.models.processing_posts import CommandsForPostsInChat
from src.services.handlers.posts.commands import CommandsPosts
from src.services.models.senders import Senders
from src.utils.logs import logging


class HandlerCommandsForPostsInChat(CommandsPosts):
    """

    Обработчик всех сообщений, связанных с постами в чатах

    """
    def handler_commands_for_posts(self, msg: str, user_id: int, chat_id: int, event: str):
        """
        Обработчик сообщений для отправки постов (чаты)

        :param msg: Текст сообщения
        :param user_id: ID пользователя, отправившего сообщение
        :param chat_id: ID чата, куда было прислано сообщение
        :param event: Событие
        """
        forward_message = self._find_command(msg)

        if forward_message:
            command = self.commands_for_posts_in_chat.get(forward_message) or self.commands_for_checking_posts.get(forward_message)

            if command["admin_only"] and chat_id == 1:
                params = self._fill_dictionary(command, chat_id, msg, user_id, event)
                try:
                    command["handler"](**params)
                except Exception as e:
                    Senders.sender(chat_id, f"Произошла ошибка при выполнении команды")
                    logging.error(f"Ошибка в команде {msg}: {e}\n{traceback.format_exc()}")

            elif not command["admin_only"] and chat_id == 5:
                try:
                    CommandsForPostsInChat.enter_post_chat(chat_id, user_id, event)
                except Exception as e:
                    Senders.sender(chat_id, f"Произошла ошибка при выполнении команды")
                    logging.error(f"Произошла ошибка при отправке поста на проверку: {e}\n{traceback.format_exc()}")

            elif not command["admin_only"] and chat_id != 5:
                Senders.sender(chat_id, f"Данное действие недоступно в текущей беседе")

    def _find_command(self, msg: str) -> str:
        """
        Поиск команды в сообщении пользователя

        :param msg: Текст сообщения
        :return: string
        """
        forward_message = None

        for cmd in self.commands_for_posts_in_chat:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        if forward_message is None:
            for _cmd in self.commands_for_checking_posts:
                if _cmd.lower() in msg.lower():
                    forward_message = _cmd

        return forward_message

    @staticmethod
    def _fill_dictionary(command: dict, chat_id: int, msg: str, user_id: int, event: str) -> dict:
        """
        Заполнение словаря параметрами

        :param command:
        :param chat_id:
        :param msg:
        :param user_id:
        :param event:
        :return: dictionary
        """
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