import logging
import time
import traceback

from vk_api import ApiError

from src.api.google_sheets.statistics import Statistics
from api.vk.vk import VkConnection
from src.database.operations.admins import Admins
from src.database.operations.posts import Posts
from src.services.general_functions import general_func
from src.services.handlers.posts import HandlerCommandsForPostsInChat

handler_commands_for_posts_in_chat = HandlerCommandsForPostsInChat()
class HandlerChatMessages:
    def __init__(self):
        """Инициализация команд для чата"""
        self.strict_commands = {
            "/cid": {
                "handler": self._cid,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/r": {
                "handler": self._reset_stats,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/admins": {
                "handler": self._admins_list,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/posts": {
                "handler": self._no_check_posts,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/fo": {
                "handler": self._info_posts_per_day,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/infopost": {
                "handler": self._info_posts_per_month,
                "admin_only": True,
                "params": ["chat_id"]
            }
        }
        self.not_strict_commands = {
            "/i": {
                "handler": self._redactors_statistics,
                "admin_only": True,
                "params": ["msg", "chat_id"]
            },
            "/ai": {
                "handler": self._redactors_statistics_for_admins,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/addmin": {
                "handler": self._add_admin,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            },
            "/deladm": {
                "handler": self._delete_admin,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            },
            "/kick": {
                "handler": self._kick_user,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            }
        }

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

    @staticmethod
    def _cid(chat_id):
        """Информация о ID текущей беседы"""
        general_func.sender(chat_id, f"ID текущей конференции: {chat_id}")

    @staticmethod
    def _kick_user(chat_id, msg, event):
        """Кик пользователя"""
        user_id = general_func.give_user_id(chat_id, msg, event)

        if user_id in Admins.get_admins_list():
            general_func.sender(chat_id, "Этот пользователь является администратором")

        elif user_id is not None:
            try:
                VkConnection.vk_api.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
            except ApiError as e:
                if e.code == 15:
                    general_func.sender(chat_id, f"Пользователь является администратором в беседе")
                if e.code == 935:
                    general_func.sender(chat_id, f"Пользователь не найден в беседе")
            except Exception as e:
                general_func.sender(chat_id, f"Данного пользователя нельзя исключить")
                logging.warning(f"Ошибка при исключении пользователя: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _reset_stats(chat_id):
        """Обнуление статистики редакторов"""
        Statistics.reset_redactors_statistics(chat_id)

    @staticmethod
    def _add_admin(chat_id, msg, event):
        user_id = general_func.give_user_id(chat_id, msg, event)

        if Admins.add_admin_to_db(user_id, chat_id) and user_id is not None:
            general_func.sender(chat_id, f"{general_func.info_user(user_id)} добавлен(а) в список администраторов")

        elif user_id in Admins.get_admins_list() and user_id is not None:
            general_func.sender(chat_id, f"{general_func.info_user(user_id)} уже есть в списке администраторов")

    @staticmethod
    def _delete_admin(chat_id, msg, event):
        """Удаление администратора (/deladm)"""
        user_id = general_func.give_user_id(chat_id, msg, event)

        if Admins.remove_admin_from_db(user_id, chat_id) and user_id is not None:
            general_func.sender(chat_id, f"{general_func.info_user(user_id)} вынесен(а) из списка администраторов")

        elif user_id not in Admins.get_admins_list() and user_id is not None:
            general_func.sender(chat_id, f"{general_func.info_user(user_id)} не найден(а) в списке администратора")

    @staticmethod
    def _admins_list(chat_id):
        start_label = f"Список администрации:\n\n"
        for cell in Admins.get_admins_list():
            if cell is None:
                continue
            elif cell.strip():
                start_label += f"{general_func.info_user(cell)}\n"

        general_func.sender(chat_id, f"{start_label}")

    @staticmethod
    def _no_check_posts(chat_id):
        """Непроверенные посты (/posts)"""
        if Posts.get_no_check_posts_list():
            ip = ""
            for i in Posts.get_no_check_posts_list():
                ip += f" #{i}"
            general_func.sender(chat_id, f"Непроверенные посты:{ip}")
        else:
            general_func.sender(chat_id, "Непроверенных постов нет")

    @staticmethod
    def _info_posts_per_day(chat_id):
        posts, approved_posts, posts_inspection = Posts.get_posts_info()
        general_func.info_posts(posts, approved_posts, posts_inspection, chat_id)

    @staticmethod
    def _redactors_statistics(msg, chat_id):
        Statistics.redactors_statistics(msg, chat_id)

    @staticmethod
    def _redactors_statistics_for_admins(chat_id):
        Statistics.redactors_statistics_for_admins(chat_id)

    @staticmethod
    def _info_posts_per_month(chat_id):
        Statistics.info_posts_per_month(chat_id)

    @staticmethod
    def thread_info_posts():
        while True:
            current_time = time.localtime()
            if current_time.tm_hour == 21 and current_time.tm_min == 0:
                posts, approved_posts, posts_inspection = Posts.get_posts_info()
                try:
                    general_func.info_posts(posts, posts_inspection, approved_posts, 6)
                    Posts.reset_posts_info()
                except Exception as e:
                    general_func.sender(2, f"Ошибка при обращении к методу: {e}")
                    logging.error(
                        f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

            time.sleep(60)
