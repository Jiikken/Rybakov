import logging
import traceback

from src.api.vk.vk import VkConnection
from src.services.models.senders import Senders


class Users(Senders):
    def give_user_id(self, chat_id, msg, event):
        """Получение chat_id пользователя из команды(Для добавления/удаления администраторов)"""
        try:
            if "id" in msg:
                first = msg.split(" ")[1]
                second = first.split("|")[0]
                user_id = second.split("[id")[1]
            elif "reply_message" in event.object.message:
                id_reply_message = event.object.message.get("reply_message")
                user_id = id_reply_message.get("from_id")
            else:
                user_id = msg.split(" ")[1]
            return user_id
        except IndexError:
            self.sender(chat_id,
                   f"Команда введена не корректно. Формат команды:\n*Команда* *ID пользователя/тег пользователя/ответ на сообщение пользователя*")
            return
        except Exception as e:
            self.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при получении ID пользователя из команды: {e}\n{traceback.format_exc()}")

    @staticmethod
    def info_user(user_id):
        """Получение имени и фамилии пользователя"""
        try:
            user_info = VkConnection.vk_api.users.get(user_ids=user_id)[0]
            first_name = user_info['first_name']
            last_name = user_info['last_name']
        except Exception as e:
            logging.error(f"Произошла ошибка при получении ID пользователя из команды: {e}\n{traceback.format_exc()}")
            return f"{user_id}"

        return f"[id{user_id}|{first_name} {last_name}]"