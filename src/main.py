import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import traceback
import threading

from vk_api.bot_longpoll import VkBotEventType

from src.utils.logs import logging
from api.vk.vk import vk_connect
from src.services.handlers.events import HandlerEvents
from src.utils.thread import ThreadModel

try:
    threading.Thread(target=ThreadModel.thread_info_posts, daemon=True).start()

    for event in vk_connect.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            HandlerEvents.handler_event(event)
except Exception as e:
    logging.critical(f"Произошла ошибка в основном потоке событий: {e}\n{traceback.format_exc()}")