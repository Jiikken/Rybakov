from src.services.handlers.chat_messages.models.chat import ChatModel
from src.services.handlers.chat_messages.models.statisctics import StatisticsModel
from src.services.handlers.chat_messages.models.admins import AdminsModel
from src.services.handlers.chat_messages.models.posts import PostsModel


class CommandsInChat(ChatModel, StatisticsModel, AdminsModel, PostsModel):
    def __init__(self):
        """Инициализация команд для чата"""
        self.strict_commands = {
            "/cid": {
                "handler": self.cid,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/r": {
                "handler": self.reset_stats,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/admins": {
                "handler": self.admins_list,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/posts": {
                "handler": self.no_check_posts,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/fo": {
                "handler": self.info_posts_per_day,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/infopost": {
                "handler": self.info_posts_per_month,
                "admin_only": True,
                "params": ["chat_id"]
            }
        }
        self.not_strict_commands = {
            "/i": {
                "handler": self.redactors_statistics,
                "admin_only": True,
                "params": ["msg", "chat_id"]
            },
            "/ai": {
                "handler": self.redactors_statistics_for_admins,
                "admin_only": True,
                "params": ["chat_id"]
            },
            "/addmin": {
                "handler": self.add_admin,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            },
            "/deladm": {
                "handler": self.delete_admin,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            },
            "/kick": {
                "handler": self.kick_user,
                "admin_only": True,
                "params": ["chat_id", "msg", "event"]
            }
        }