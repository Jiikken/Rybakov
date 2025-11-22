import traceback

from src.utils.logs import logging
from src.services.handlers.chat_messages import HandlerChatMessages
from src.services.handlers.ls_messages import HandlerLSMessages

handler_chat_messages = HandlerChatMessages()
handler_ls_messages = HandlerLSMessages()
class HandlerEvents:
    def __init__(self, event):
        """Инициализация временных переменных"""
        try:
            self.chat_id = event.chat_id
            self.user_id = event.message.get("from_id")
            self.msg = event.object.message["text"]
        except Exception as e:
            logging.error(f"Ошибка при получении временных переменных: {e}\n{traceback.format_exc()}")

    def handler_event(self, event):
        if event.from_chat:
            handler_chat_messages.handler_chat_message(self.msg, self.user_id, self.chat_id, event)
        elif event.from_user:
            handler_ls_messages.handler_ls_messages(self.msg, self.user_id, self.chat_id, event)
