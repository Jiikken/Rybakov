import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import traceback
import threading

from vk_api.bot_longpoll import VkBotEventType

from src.utils.logs import logging
from src.api.vk import vk
from src.services.handlers.events import HandlerEvents
from src.services.handlers.chat_messages import HandlerChatMessages


try:
    threading.Thread(target=HandlerChatMessages().thread_info_posts, daemon=True).start()

    for event in vk.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            HandlerEvents(event).handler_event(event)
except Exception as e:
    logging.critical(f"Произошла ошибка в основном потоке событий: {e}\n{traceback.format_exc()}")