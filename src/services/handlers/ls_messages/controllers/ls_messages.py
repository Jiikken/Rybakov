import logging
import traceback

from src.services.handlers.ls_messages.commands import CommandsInLS
from src.services.handlers.ls_messages.models.send_images import SendImagesModel
from src.services.handlers.posts.ls.controllers.handler_posts import handler_commands_for_posts_in_ls
from src.services.models.senders import Senders
from src.services.models.users import Users
from src.utils.keyboards import Keyboards


class HandlerLSMessages(CommandsInLS):
    def handler_ls_message(self, msg: str, user_id: int, event: str):
        """
        Обработчик сообщений в ЛС

        :param user_id: ID пользователя, от которого произошло событие
        :param msg: Сообщение из события
        :param event: Событие
        """
        print(163)
        forward_message = self._find_command(msg)
        print(2)
        if forward_message is None:
            handler_commands_for_posts_in_ls.handler_commands_for_posts()

        if forward_message:
            print(3)
            command = self.commands_for_posts_admin.get(forward_message)
            try:
                command["handler"](user_id, event)
            except Exception as e:
                Senders.sender_in_ls(user_id, f"Произошла ошибка при обращении к методу")
                logging.error(f"Ошибка при выполнении команды {forward_message}: {e}\n{traceback.format_exc()}")

        elif msg.lower() == "хочу":
            SendImagesModel.send_cheburek(user_id)
        elif msg.lower() == "пельмень":
            SendImagesModel.send_dikiy_ogyrec(user_id)
        else:
            print(4)
            Senders.sender_in_ls(user_id, f"Здравствуйте, {Users.info_user(user_id)}\n\nХотите чебурек?", keyboard=Keyboards.cheburek())

    def _find_command(self, msg: str) -> str:
        """
        Поиск команды из сообщения пользователя

        :param msg: Сообщение из события
        :return: string
        """
        forward_message = None

        for cmd in self.commands_for_posts_admin:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        return forward_message

handler_ls_messages = HandlerLSMessages()