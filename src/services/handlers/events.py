import traceback

from src.utils.logs import logging
from src.services.handlers.chat_messages.controllers.chat_messages import handler_chat_messages
from src.services.handlers.ls_messages.controllers.ls_messages import handler_ls_messages


class HandlerEvents:
    @staticmethod
    def handler_event(event):
        try:
            chat_id = event.chat_id
            user_id = event.message.get("from_id")
            msg = event.object.message["text"]
            if event.from_chat:
                handler_chat_messages.handler_chat_message(msg, user_id, chat_id, event)
            elif event.from_user:
                handler_ls_messages.handler_ls_messages(msg, user_id, chat_id, event)
        except Exception as e:
            logging.error(f"Ошибка при обработке события: {e}\n{traceback.format_exc()}")

