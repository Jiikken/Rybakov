import json
import traceback
from datetime import datetime
from typing import Optional

from babel.dates import format_date
from vk_api import ApiError

from api.vk.vk import VkConnection
from src.utils.logs import logging


class GeneralFunctions:
    def sender(self, chat_id: int, text: str, mid: Optional[str] = None, keyboard: Optional[str] = None):
        try:
            VkConnection.vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0, 'forward': mid, 'keyboard': keyboard})
        except ApiError as a:
            if a.code == 100:
                self.sender(chat_id, f"Перешлите это сообщение Кириллу")
        except Exception as e:
            self.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(sender): {e}\n{traceback.format_exc()}")

    def sender_in_ls(self, user_id: int, text: str, mid: Optional[str] = None, keyboard: Optional[str] = None, attachment = None):
        try:
            VkConnection.vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': 0, 'attachment': attachment, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            self.sender(user_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(sender_in_ls): {e}\n{traceback.format_exc()}")

    def resend_in_ls(self, chat_id: int, text: str, mid: Optional[str], keyboard = None):
        """resend message from ls"""
        try:
            VkConnection.vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0, 'forward_messages': mid, 'keyboard': keyboard})
        except Exception as e:
            self.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Произошла ошибка при отправке сообщения(resend_in_ls): {e}\n{traceback.format_exc()}")

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

    def info_posts(self, posts, approved_posts, posts_inspection, chat_id):
        """Информация о постах(/fo)"""
        try:
            current_date = datetime.now()

            if posts_inspection > 0 or approved_posts > 0 or posts > 0:
                day = current_date.day
                month = format_date(current_date, format='MMMM', locale='ru_RU')

                # Рассчитываем процент одобрения только если есть одобренные посты
                approved_percent_def = approved_posts / posts * 100 if posts and approved_posts else 0
                result_def = round(approved_percent_def, 1) if posts and approved_posts else 0

                posts_check = f'Постов отправлено на проверку: {max(posts, posts_inspection)}\n'
                dont_check_posts = f'Непроверенные посты: {posts_inspection}\n' if posts_inspection > 0 else ''
                approved_posts_check = f'Постов одобрено: {approved_posts}\n' if posts > 0 else ''
                percent_approved_posts = f'Процент одобрения: {result_def}%' if posts > 0 else ''

                info = f'Статистика работы редакторов за {day} {month}:\n\n'
                info += posts_check

                if posts_inspection > 0:
                    info += dont_check_posts
                info += approved_posts_check
                info += percent_approved_posts

                self.sender(chat_id, info)

            else:
                self.sender(chat_id, 'Мне очень жаль об этом говорить, но сегодня не было ни одного поста на проверку😔')
        except Exception as e:
            self.sender(chat_id, f"Не могу отправить информацию о постах за сегодня из-за того, что разработчик реализовал этот метод неправильно\n\nНадеюсь, что к завтрашнему дню он всё исправит")
            logging.error(f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

    def get_post_id_from_message(self, chat_id, msg):
        """Получение chat_id сообщения по числу в сообщении"""
        try:
            if "@rybakovbot" in msg:
                message_id = int(msg.split(' ')[2])
            else:
                message_id = int(msg.split(' ')[1])
        except IndexError:
            self.sender(chat_id, f"Укажите номер поста, на который даёте вердикт")
            message_id = 0
        except ValueError:
            self.sender(chat_id, f"Номер поста должен быть числом")
            message_id = 0

        return message_id

    def get_post_id_from_message_for_personal_response(self, chat_id, msg):
        """Получение chat_id сообщения по числу в сообщении"""
        try:
            if "@rybakovbot" in msg:
                message_id = int(msg.split(' ')[3])
            else:
                message_id = int(msg.split(' ')[2])
        except IndexError:
            self.sender(chat_id, f"Укажите номер поста, на который даёте вердикт")
            message_id = 0
        except ValueError:
            self.sender(chat_id, f"Номер поста должен быть числом")
            message_id = 0

        return message_id

    def get_midd(self, msg, chat_id, message_from_chat = 5):
        """Получение пересылаемого JSON для пересылки сообщения"""
        try:
            midd = json.dumps(
                {'peer_id': 2000000000 + message_from_chat, 'conversation_message_ids': self.get_post_id_from_message(chat_id, msg),
                 'is_reply': False})
        except Exception as e:
            logging.error(f"Произошла ошибка при нахождения midd: {e}\n{traceback.format_exc()}")
            midd = None

        return midd

general_func = GeneralFunctions()