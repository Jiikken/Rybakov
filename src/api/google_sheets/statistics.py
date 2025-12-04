import logging
import threading
import traceback
from datetime import datetime
from typing import Optional

from src.api.google_sheets.connection import GoogleSheets
from src.services.models.senders import Senders


class Statistics(GoogleSheets):
    def redactors_statistics(self, msg: Optional[str], chat_id: int):
        """Получение статистики редакторов"""
        try:
            self.rate_limit()
            days = self.manager.days

            select_days = self._validation_days_since_restart(msg, days.days_since_reset_stats, chat_id)
            posts_stats = self._get_stats_about_posts(msg, select_days)
            statistics = self._formation_statistics_message(msg, select_days, posts_stats)

            Senders.sender(chat_id, statistics)

        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов: {e}\n{traceback.format_exc()}")

    def _validation_days_since_restart(self, msg: str, days_since_restart: int, chat_id: int) -> int:
        """
        Проверка введённых дней для сбора статистики

        :param msg
        :param days_since_restart
        :param chat_id

        :return: select days
        """
        days = self.manager.days

        if len(msg.split(" ")) > 1:
            try:
                select_days = int(msg.split(" ")[1])
                if select_days > days_since_restart:
                    Senders.sender(chat_id, f"Информации за этот период ещё нет (максимум дней: {days_since_restart})")
                    raise ValueError("Введено число превышающее истинное значение")
                if select_days < 0:
                    Senders.sender(chat_id, f"Не могу показать информацию за минусовой период")
                    raise ValueError("Введено число отрицательное число")
            except ValueError:
                Senders.sender(chat_id, "Не могу отправить статистику за данный период")
                raise ValueError("Что-то введено неверно")
        else:
            select_days = days.days_since_reset_stats

        return select_days


    def _get_stats_about_posts(self, msg:str, select_days: int) -> list:
        """
        Получение информации о постах за выбранных период из таблицы

        :param msg:
        :param select_days:

        :return: post_stats
        """

        sheets = self.manager.sheets
        redactors = self.manager.redactors_info
        days = self.manager.days
        posts_stats = [0] * len(redactors.ids)

        if len(msg.split(" ")) > 1:
            start_col = 2 + (days.days_since_reset_stats - select_days + 1)
            end_col = 2 + days.days_since_reset_stats

            for col in range(start_col, end_col + 1):
                day_posts = sheets.stability.col_values(col)[1:]
                for i in range(len(redactors.ids)):
                    try:
                        posts_stats[i] += int(day_posts[i]) if i < len(day_posts) and str(day_posts[i]).isdigit() else 0
                    except (IndexError, ValueError):
                        continue
        else:
            current_posts = redactors.statistics

            for i in range(len(redactors.ids)):
                posts_stats[i] = int(current_posts[i]) if i < len(current_posts) and str(
                    current_posts[i]).isdigit() else 0

        return posts_stats

    def _formation_statistics_message(self, msg: str, select_days: int, posts_stats: list) -> str:
        """
        Формирование сообщения статистики редакторов

        :param msg:
        :param select_days:
        :param posts_stats:

        :return: statistics
        """
        redactors = self.manager.redactors_info
        days = self.manager.days

        word_info = "Редактор — [ СТАТИСТИКА ]" if days.days_since_reset_stats >= 10 and len(msg.split(" ")) == 1 else "Редактор — [ Всего постов отправлено ]"

        statistics = f"Статистика редакторов за выбранное количество дней: {select_days}\n\n"
        statistics += f"{word_info}\n\n"

        # Перебор всех редакторов
        for index, redactor_id in enumerate(redactors.ids):
            redactor_id = redactor_id.strip()
            if redactor_id.isdigit():

                # Сбор информации о редакторе
                redactors_statistics = redactors.statistics[index] if index < len(redactors.statistics) else 0
                posts_sent_for_review = redactors.posts_sent_for_review[index] if index < len(redactors.posts_sent_for_review) else 0
                redactor_probation = redactors.probation[index].strip() if index < len(redactors.probation) else ""

                posts_count = posts_stats[index] if len(msg.split(" ")) > 1 else posts_sent_for_review

                # Формирование сообщения о редакторе
                if index < len(redactors.names):
                    if select_days >= 10 and len(msg.split(" ")) < 2:
                        if redactor_probation:
                            statistics += f"{redactor_probation} [id{redactor_id}|{redactors.names[index]}] — [ {redactors_statistics} ]\n"
                        else:
                            statistics += f"[id{redactor_id}|{redactors.names[index]}] — [ {redactors_statistics} ]\n"
                    else:
                        if redactor_probation:
                            statistics += f"{redactor_probation} [id{redactor_id}|{redactors.names[index]}] — [ {posts_count} ]\n"
                        else:
                            statistics += f"[id{redactor_id}|{redactors.names[index]}] — [ {posts_count} ]\n"

        return statistics

    def redactors_statistics_for_admins(self, chat_id: int):
        """Получение статистики редакторов для администрации"""
        try:
            self.rate_limit()

            statistics = self._formation_statistics_message_for_admins()

            Senders.sender(chat_id, statistics)
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов для администрации: {e}\n{traceback.format_exc()}")

    def _formation_statistics_message_for_admins(self) -> str:
        redactors = self.manager.redactors_info
        days = self.manager.days

        statistics = (
            f"Статистика редакторов за выбранное количество дней: {days.days_since_reset_stats}\n\n"
            f"Редактор — [ Опубликовано | Всего | % Одобрения ] \n\n"
        )

        # Перебор всех редакторов
        for index, redactor_id in enumerate(redactors.ids):
            print(index, redactor_id, redactors.ids)
            redactor_id = redactor_id.strip()
            if redactor_id.isdigit():

                # Сбор информации о редакторе
                all_posts = redactors.all_posts[index] if index < len(redactors.all_posts) else 0
                percent_approved_posts = redactors.percent_approved_posts[index] if index < len(redactors.percent_approved_posts) else 0
                posts_sent_for_review = redactors.posts_sent_for_review[index] if index < len(redactors.posts_sent_for_review) else 0
                redactor_probation = redactors.probation[index].strip() if index < len(redactors.probation) else ""

                # Формирование строки редактора
                if index < len(redactors.names):
                    if redactor_probation:
                        statistics += f"{redactor_probation} [id{redactor_id}|{redactors.names[index]}] — [ {all_posts} | {posts_sent_for_review} | {percent_approved_posts} ]\n"
                    else:
                        statistics += f"[id{redactor_id}|{redactors.names[index]}] — [ {all_posts} | {posts_sent_for_review} | {percent_approved_posts} ]\n"

        return statistics

    def reset_redactors_statistics(self, chat_id: int):
        """Обнуление статистики (/r)"""
        try:
            self.rate_limit()

            threading.Thread(target=self._reset_statistics_thread, args=(chat_id,), daemon=True).start()

        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при сбросе статистики: {e}\n{traceback.format_exc()}")

    def _reset_statistics_thread(self, chat_id: int):
        """Работа с таблицами в отдельном потоке"""
        sheets = self.manager.sheets

        sheets.bot_sheet.update_acell("B33", datetime.now().strftime("%d.%m.%Y"))

        sheets.bot_sheet.batch_clear(["C2:C"])
        sheets.work_sheet.batch_clear(["A2:E"])
        sheets.work_sheet.batch_clear(["G2:G"])

        # Получаем размер диапазона
        range_info = sheets.stability.get("C2:AH")
        rows = len(range_info) if range_info else 1
        cols = 32

        # Заполняем нулями
        zero_matrix = [[0] * cols for _ in range(rows)]
        sheets.stability.update("C2:AH", zero_matrix)

        Senders.sender(chat_id, "Статистика обнулена")

statistics_from_gs = Statistics()