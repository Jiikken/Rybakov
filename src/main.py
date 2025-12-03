import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import traceback
import threading

from vk_api.bot_longpoll import VkBotEventType

from src.utils.logs import logging
from api.vk.vk import VkConnection
from src.services.handlers.events import HandlerEvents
from src.utils.thread import ThreadModel
from src.api.google_sheets.init import GoogleSheets


try:
    threading.Thread(target=ThreadModel.thread_info_posts, daemon=True).start()

    for i in range(1):
        GoogleSheets()

    for event in VkConnection.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            HandlerEvents.handler_event(event)
except Exception as e:
    logging.critical(f"Произошла ошибка в основном потоке событий: {e}\n{traceback.format_exc()}")