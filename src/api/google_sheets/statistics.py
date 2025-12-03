import logging
import threading
import traceback
from datetime import datetime
from typing import Optional

from src.api.google_sheets.init import GoogleSheets
from src.services.models.senders import Senders


class Statistics(GoogleSheets):
    def redactors_statistics(self, msg: Optional[str], chat_id: int):
        """Получение статистики редакторов"""
        try:
            self.rate_limit()
            sheets = self.get_sheets()
            columns = self.get_columns()

            if len(msg.split(" ")) > 1:
                select_days = self._validation_days_since_restart(msg, columns["days_since_restart"], chat_id)
            else:
                select_days = columns["days_since_restart"]

            # Инициализация статистики
            posts_stats = [0] * len(columns["ids"])

            # Если выбран период - собираем статистику по постам
            if len(msg.split(" ")) > 1:
                posts_stats = self._get_stats_about_posts(columns, select_days, sheets, posts_stats)
            else:
                current_posts = columns["statistics"]

                for i in range(len(columns["ids"])):
                    posts_stats[i] = int(current_posts[i]) if i < len(current_posts) and str(current_posts[i]).isdigit() else 0

            statistics = f"{self._formation_statistics_message(columns, msg, select_days, posts_stats)}"

            Senders.sender(chat_id, statistics)

        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _validation_days_since_restart(msg: str, days_since_restart: int, chat_id: int) -> int:
        """
        Проверка введённых дней для сбора статистики

        :param msg
        :param days_since_restart
        :param chat_id

        :return: select days
        """
        try:
            select_days = int(msg.split(" ")[1])
            if select_days > days_since_restart:
                Senders.sender(chat_id, f"Информации за этот период ещё нет (максимум дней: {days_since_restart})")
                raise ValueError("Введено число превышающее истинное значение")
            if select_days < 0:
                Senders.sender(chat_id, f"Не могу показать информацию за минусовой период")
                raise ValueError("Введено число отрицательное число")
            return select_days
        except ValueError:
            Senders.sender(chat_id, "Не могу отправить статистику за данный период")
            raise ValueError("Что-то введено неверно")

    @staticmethod
    def _get_stats_about_posts(columns: dict, select_days: int, sheets: dict, posts_stats: list) -> list:
        """
        Получение информации о постах за выбранных период из таблицы

        :param columns:
        :param select_days:
        :param sheets:
        :param posts_stats:

        :return: post_stats
        """
        start_col = 2 + (columns["days_since_restart"] - select_days + 1)
        end_col = 2 + columns["days_since_restart"]

        for col in range(start_col, end_col + 1):
            day_posts = sheets["stability"].col_values(col)[1:]
            for i in range(len(columns["ids"])):
                try:
                    posts_stats[i] += int(day_posts[i]) if i < len(day_posts) and str(day_posts[i]).isdigit() else 0
                except (IndexError, ValueError):
                    continue

        return posts_stats

    @staticmethod
    def _formation_statistics_message(columns: dict, msg: str, select_days: int, posts_stats: list) -> str:
        """
        Формирование сообщения статистики редакторов

        :param msg:
        :param select_days:
        :param posts_stats:

        :return: statistics
        """
        word_info = "Редактор — [ СТАТИСТИКА ]" if columns["days_since_restart"] >= 10 and len(msg.split(" ")) == 1 else "Редактор — [ Всего постов отправлено ]"

        statistics = f"Статистика редакторов за выбранное количество дней: {select_days}\n\n"
        statistics += f"{word_info}\n\n"

        # Перебор всех редакторов
        for index, redactor_id in enumerate(columns["ids"]):
            redactor_id = redactor_id.strip()
            if redactor_id.isdigit():

                # Сбор информации о редакторе
                redactors_statistics = columns['statistics'][index] if index < len(columns['statistics']) else 0
                posts_sent_for_review = columns['posts_sent_for_review'][index] if index < len(columns['posts_sent_for_review']) else 0
                redactor_probation = columns['probation'][index].strip() if index < len(columns['probation']) else ""

                posts_count = posts_stats[index] if len(msg.split(" ")) > 1 else posts_sent_for_review

                # Формирование сообщения о редакторе
                if index < len(columns["names"]):
                    if select_days >= 10 and len(msg.split(" ")) < 2:
                        if redactor_probation:
                            statistics += f"{redactor_probation} [id{redactor_id}|{columns['names'][index]}] — [ {redactors_statistics} ]\n"
                        else:
                            statistics += f"[id{redactor_id}|{columns['names'][index]}] — [ {redactors_statistics} ]\n"
                    else:
                        if redactor_probation:
                            statistics += f"{redactor_probation} [id{redactor_id}|{columns['names'][index]}] — [ {posts_count} ]\n"
                        else:
                            statistics += f"[id{redactor_id}|{columns['names'][index]}] — [ {posts_count} ]\n"

            return statistics

    def redactors_statistics_for_admins(self, chat_id: int):
        """Получение статистики редакторов для администрации"""
        try:
            self.rate_limit()
            columns = self.get_columns()

            statistics = self._formation_statistics_message_for_admins(columns)

            Senders.sender(chat_id, statistics)
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов для администрации: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _formation_statistics_message_for_admins(columns: dict) -> str:
        statistics = (
            f"Статистика редакторов за выбранное количество дней: {columns["days_since_restart"]}\n\n"
            f"Редактор — [ Опубликовано | Всего | % Одобрения ] \n\n"
        )

        # Перебор всех редакторов
        for index, redactor_id in enumerate(columns["ids"]):
            redactor_id = redactor_id.strip()
            if redactor_id.isdigit():

                # Сбор информации о редакторе
                all_posts = columns["all_posts"][index] if index < len(columns["all_posts"]) else 0
                percent_approved_posts = columns["percent_approved_posts"][index] if index < len(columns["percent_approved_posts"]) else 0
                posts_sent_for_review = columns["posts_sent_for_review"][index] if index < len(columns["posts_sent_for_review"]) else 0
                redactor_probation = columns["probation"][index].strip() if index < len(columns["probation"]) else ""

                # Формирование строки редактора
                if index < len(columns["names"]):
                    if redactor_probation:
                        statistics += f"{redactor_probation} [id{redactor_id}|{columns["names"][index]}] — [ {all_posts} | {posts_sent_for_review} | {percent_approved_posts} ]\n"
                    else:
                        statistics += f"[id{redactor_id}|{columns["names"][index]}] — [ {all_posts} | {posts_sent_for_review} | {percent_approved_posts} ]\n"

        return statistics

    def reset_redactors_statistics(self, chat_id: int):
        """Обнуление статистики (/r)"""
        try:
            self.rate_limit()

            threading.Thread(target=self._reset_statistics_thread, daemon=True).start()

            Senders.sender(chat_id, "Статистика обнулена")
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при сбросе статистики: {e}\n{traceback.format_exc()}")

    def _reset_statistics_thread(self):
        """Работа с таблицами в отдельном потоке"""
        sheets = self.get_sheets()

        sheets["bot_sheet"].update_acell("B33", datetime.now().strftime("%d.%m.%Y"))

        sheets["bot_sheet"].batch_clear(["C2:C"])
        sheets["redactors_sheet"].batch_clear(["A2:E"])
        sheets["redactors_sheet"].batch_clear(["G2:G"])

        # Получаем размер диапазона
        range_info = sheets["stability"].get("C2:AH")
        rows = len(range_info) if range_info else 1
        cols = 32

        # Заполняем нулями
        zero_matrix = [[0] * cols for _ in range(rows)]
        sheets["stability"].update("C2:AH", zero_matrix)

statistics_from_gs = Statistics()