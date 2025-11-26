import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import traceback
import threading

from vk_api.bot_longpoll import VkBotEventType

from src.utils.logs import logging
from api.vk.vk import VkConnection
from src.services.handlers.events import HandlerEvents
from services.handlers.chat_messages.controllers.chat_messages import HandlerChatMessages


try:
    threading.Thread(target=HandlerChatMessages().thread_info_posts, daemon=True).start()

    for event in VkConnection.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            HandlerEvents(event).handler_event(event)
except Exception as e:
    logging.critical(f"Произошла ошибка в основном потоке событий: {e}\n{traceback.format_exc()}")