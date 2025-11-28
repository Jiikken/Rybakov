import logging
import traceback

from datetime import datetime
from babel.dates import format_date

from src.services.models.senders import Senders


class Posts(Senders):
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