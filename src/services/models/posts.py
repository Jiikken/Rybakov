import json
import logging
import time
import traceback
from datetime import datetime

from babel.dates import format_date
from vk_api.bot_longpoll import VkBotEventType

from src.api.vk.vk import VkConnection
from src.database.operations.post_and_user import post_and_user
from src.services.models.senders import Senders


class Posts(Senders):
    def info_posts(self, posts: int, approved_posts: int, posts_inspection: int, chat_id: int):
        """
        Информация о постах за день (/fo)

        :param posts: Кол-во всех отправленных постов на проверку
        :param approved_posts: Кол-во всех одобренных постов
        :param posts_inspection: Кол-во непроверенных постов
        :param chat_id: ID чата
        """
        try:
            if posts_inspection > 0 or approved_posts > 0 or posts > 0:
                result_def = self._calculate_statistics_posts(posts, approved_posts)

                info = self._formation_message_about_statistics_posts(posts, approved_posts, posts_inspection, result_def)

                self.sender(chat_id, info)
            else:
                self.sender(chat_id, 'Мне очень жаль об этом говорить, но сегодня не было ни одного поста на проверку😔')
        except Exception as e:
            self.sender(chat_id, f"Не могу отправить информацию о постах за сегодня из-за того, что разработчик реализовал этот метод неправильно\n\nНадеюсь, что к завтрашнему дню он всё исправит")
            logging.error(f"Произошла ошибка при отправке информации о постах за день: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _calculate_statistics_posts(posts: int, approved_posts: int) -> int:
        """
        Подсчёт процента одобренных постов за день

        :param posts: Кол-во всех отправленных постов на проверку
        :param approved_posts: Кол-во всех одобренных постов
        :return: int
        """
        try:
            approved_percent_def = approved_posts / posts * 100 if posts and approved_posts else 0
            result_def = round(approved_percent_def, 1) if posts and approved_posts else 0
            return result_def
        except Exception as e:
            logging.error(f"Ошибка при подсчёте процента одобрения: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _formation_message_about_statistics_posts(posts: int, approved_posts: int, posts_inspection: int, result_def: int) -> str:
        """
        Формирование сообщения о статистике постов за день

        :param posts: Кол-во всех отправленных постов на проверку
        :param approved_posts: Кол-во всех одобренных постов
        :param posts_inspection: Кол-во непроверенных постов
        :param result_def: Процент одобрения постов
        :return: string
        """
        try:
            current_date = datetime.now()
            day = current_date.day
            month = format_date(current_date, format='MMMM', locale='ru_RU')

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

            return info
        except Exception as e:
            logging.error(f"Ошибка при формировании сообщения: {e}\n{traceback.format_exc()}")

    def get_post_id_from_message(self, chat_id: int, msg: str) -> int:
        """
        Получение message_id по сообщению

        :param chat_id: ID чата
        :param msg: Текст сообщения
        :return: int
        """
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

    def get_post_id_from_message_for_personal_response(self, chat_id: int, msg: str):
        """
        Получение message_id по сообщению (для персонального ответа)

        :param chat_id: ID чата
        :param msg: Текст сообщения
        :return: int
        """
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

    @staticmethod
    def wait_for_user_input(chat_id: int, message_id: str, timeout: int = 60) -> str:
        """
        Ожидание персонального ответа от администратора

        :param chat_id: ID чата
        :param message_id: Текст сообщения
        :param timeout: Время ожидания (По умолчанию 60 секунд)
        :return: string
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            for event in VkConnection.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat and event.chat_id == chat_id:
                        user_id = event.message.get("from_id")
                        if user_id == post_and_user.get_admin_id_by_response_post(message_id):
                            user_response = event.object.message['text']
                            return user_response

        Senders.sender(chat_id, 'Время ожидания истекло')
        return "нужно переделать этот пост ;)"

    @staticmethod
    def get_midd(msg: str, chat_id: int, message_from_chat: int = 5):
        """
        Получение пересылаемого JSON для пересылки сообщения

        :param msg: Текст сообщения
        :param chat_id: ID чата, для того, чтобы узнать ID сообщения
        :param message_from_chat: ID чата, от куда сообщение (по умолчанию 5)
        :return:
        """
        try:
            midd = json.dumps(
                {'peer_id': 2000000000 + message_from_chat,
                 'conversation_message_ids': info_about_posts_in_chat.get_post_id_from_message(chat_id, msg),
                 'is_reply': False})
        except Exception as e:
            logging.error(f"Произошла ошибка при нахождения midd: {e}\n{traceback.format_exc()}")
            midd = None

        return midd

info_about_posts_in_chat = Posts()