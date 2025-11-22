import logging
import traceback
from datetime import datetime
from typing import Optional

import time
import gspread
from google.oauth2.service_account import Credentials
from vk_api import ApiError

from src.config import config
from src.services.general_functions import general_func


class GoogleSheets:
    def __init__(self):
        """Подключение к Google Sheets"""
        try:
            self.scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            self.creds = Credentials.from_service_account_file(config.credentials_path, scopes=self.scope)
            self.client = gspread.authorize(self.creds)
            logging.info(f"Подключение к Google Sheets успешно")
            self.last_request_time = 0
            self.min_interval = 1.0  # Минимальная задержка между запросами в секундах
        except Exception as e:
            logging.error(f"Произошла ошибка при подключении к Google Sheets: {e}\n{traceback.format_exc()}")

    def _rate_limit(self):
        """Ограничение частоты запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

    def _get_sheet_with_retry(self, sheet_name=None, max_retries=3):
        """Получение листа с повторными попытками"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                return self.client.open(config.spreadsheetname).worksheet(
                    sheet_name if sheet_name else config.default_sheet_name
                )
            except ApiError as e:
                if '429' in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1  # Экспоненциальная backoff
                    logging.warning(f"Rate limit exceeded, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

    def _get_sheet(self, sheet_name: Optional[str] = None):
        """Получение таблицы по названию"""
        return self.client.open(config.spreadsheetname).worksheet(sheet_name if sheet_name else config.default_sheet_name)

    def redactors_statistics(self, msg: Optional[str], chat_id: int):
        """Получение статистики редакторов"""
        try:
            self._rate_limit()
            main_stats_sheet = self._get_sheet("Статистика")
            stats_for_select_days = self._get_sheet("Стабильность")
            bot_sheet = self._get_sheet("Информация для бота")

            days_since_restart = int(bot_sheet.acell("B32").value)

            if len(msg.split(" ")) > 1:
                try:
                    select_days = int(msg.split(" ")[1])
                    if select_days > days_since_restart:
                        general_func.sender(chat_id, f"Информации за этот период ещё нет (максимум дней: {days_since_restart})")
                        return
                    if select_days < 0:
                        general_func.sender(chat_id, f"Не могу показать информацию за минусовой период")
                        return
                except ValueError:
                    general_func.sender(chat_id, "Не могу отправить статистику за данный период")
                    return
            else:
                select_days = days_since_restart

            # Получаем данные по найденным индексам
            redactors_ids = main_stats_sheet.col_values(10)[1:] # IDs редакторов
            redactors_names = main_stats_sheet.col_values(2)[1:] # Имена ВК
            probation = main_stats_sheet.col_values(11)[1:] # Должность
            redactors_statistics = main_stats_sheet.col_values(8)[1:] # Статистика

            posts_sent_for_review = bot_sheet.col_values(2)[1:] # Опубликованных по

            # Инициализация статистики
            post_stats = [0] * len(redactors_ids)

            # Если выбран период - собираем статистику по постам
            if len(msg.split(" ")) > 1:
                start_col = 2 + (days_since_restart - select_days + 1)
                end_col = 2 + days_since_restart

                # Собираем данные из всех столбцов периода
                for col in range(start_col, end_col + 1):
                    day_posts = stats_for_select_days.col_values(col)[1:]
                    for i in range(len(redactors_ids)):
                        try:
                            post_stats[i] += int(day_posts[i]) if i < len(day_posts) and str(day_posts[i]).isdigit() else 0
                        except (IndexError, ValueError):
                            continue
            else:
                # Текущая статистика (из столбца I)
                current_posts = redactors_statistics  # Столбец I

                for i in range(len(redactors_ids)):
                    post_stats[i] = int(current_posts[i]) if i < len(current_posts) and str(current_posts[i]).isdigit() else 0

            word_info = "Редактор — [ СТАТИСТИКА ]" if days_since_restart >= 10 and len(msg.split(" ")) == 1 else "Редактор — [ Всего постов отправлено ]"

            statistics = f"Статистика редакторов за выбранное количество дней: {select_days}\n\n"
            statistics += f"{word_info}\n\n"

            for index, redactor_id in enumerate(redactors_ids):
                redactor_id = redactor_id.strip()
                if redactor_id.isdigit():  # Проверяем, что chat_id пользователя корректный
                    rc = redactors_statistics[index] if index < len(redactors_statistics) else 0
                    pp = posts_sent_for_review[index] if index < len(posts_sent_for_review) else 0
                    additional_text = probation[index].strip() if index < len(probation) else ""

                    # Используем post_stats если выбран период, иначе pp
                    posts_count = post_stats[index] if len(msg.split(" ")) > 1 else pp

                    # Проверяем, что индекс не выходит за пределы списка subscribers_names
                    if index < len(redactors_names):
                        if select_days >= 10 and len(msg.split(" ")) < 2:
                            if additional_text:  # Проверяем, есть ли текст в 10-м столбце
                                statistics += f"{additional_text} [id{redactor_id}|{redactors_names[index]}] — [ {rc} ]\n"
                            else:
                                statistics += f"[id{redactor_id}|{redactors_names[index]}] — [ {rc} ]\n"
                        else:
                            if additional_text:  # Проверяем, есть ли текст в 10-м столбце
                                statistics += f"{additional_text} [id{redactor_id}|{redactors_names[index]}] — [ {posts_count} ]\n"
                            else:
                                statistics += f"[id{redactor_id}|{redactors_names[index]}] — [ {posts_count} ]\n"

            general_func.sender(chat_id, statistics)

        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов: {e}\n{traceback.format_exc()}")

    def redactors_statistics_for_admins(self, chat_id: int):
        """Получение статистики редакторов для администрации"""
        try:
            self._rate_limit()
            main_stats_sheet = self._get_sheet("Статистика")
            bot_sheet = self._get_sheet("Информация для бота")

            days_since_restart = int(bot_sheet.acell("B32").value)

            redactors_ids = bot_sheet.col_values(1)[1:]  # IDs редакторов
            redactors_names = main_stats_sheet.col_values(2)[1:]  # Имена ВК
            probation = main_stats_sheet.col_values(11)[1:]  # Должность
            posts_sent_for_review = bot_sheet.col_values(2)[1:]  # Опубликованных по
            all_posts = main_stats_sheet.col_values(6)[1:]  # Все посты из столбца F
            percent_approved_posts = main_stats_sheet.col_values(9)[1:]  # Процент одобрения из столбца K

            statistics = (
                f"Статистика редакторов за выбранное количество дней: {days_since_restart}\n\n"
                f"Редактор — [ Опубликовано | Всего | % Одобрения ] \n\n"
            )

            for index, subscriber_id in enumerate(redactors_ids):
                subscriber_id = subscriber_id.strip()
                if subscriber_id.isdigit():  # Проверяем, что chat_id пользователя корректный
                    ap = all_posts[index] if index < len(all_posts) else 0
                    pap = percent_approved_posts[index] if index < len(percent_approved_posts) else 0
                    pp = posts_sent_for_review[index] if index < len(posts_sent_for_review) else 0
                    additional_text = probation[index].strip() if index < len(probation) else ""

                    # Проверяем, что индекс не выходит за пределы списка subscribers_names
                    if index < len(redactors_names):
                        if additional_text:  # Проверяем, есть ли текст в 10-м столбце
                            statistics += f"{additional_text} [id{subscriber_id}|{redactors_names[index]}] — [ {ap} | {pp} | {pap} ]\n"
                        else:
                            statistics += f"[id{subscriber_id}|{redactors_names[index]}] — [ {ap} | {pp} | {pap} ]\n"

            general_func.sender(chat_id, statistics)
        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов для администрации: {e}\n{traceback.format_exc()}")

    def summ_posts(self, user_id: int, chat_id: int = 2):
        """Метод для статистики количества постов отправленных от пользователя"""
        try:
            self._rate_limit()
            bot_sheet = self._get_sheet("Информация для бота")
            stats_for_select_days = self._get_sheet("Стабильность")

            day_reset_stats = bot_sheet.acell("B32")
            redactors_ids = stats_for_select_days.col_values(2)[1:]
            days_reset_stats = stats_for_select_days.row_values(1)

            for index, redactor_id in enumerate(redactors_ids):
                redactor_id = redactor_id.strip()

                if redactor_id.isdigit():
                    if str(user_id) == str(redactor_id):
                        for i in days_reset_stats:
                            if day_reset_stats.value == i:
                                current_count = int(stats_for_select_days.cell(index + 2, int(i) + 2).value)
                                new_value = current_count + 1

                                stats_for_select_days.update_cell(index + 2, int(i) + 2, new_value)

        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при суммировании поста: {e}\n{traceback.format_exc()}")

    def summ_approved_posts(self, user_id, chat_id):
        try:
            self._rate_limit()
            bot_sheet = self._get_sheet("Информация для бота")

            redactors_ids = bot_sheet.col_values(1)[1:]
            column_percent_approved_posts = int(bot_sheet.row_values(1).index("Одобренные посты") + 1)

            for i, value in enumerate(redactors_ids):
                if str(user_id) == str(value):

                    # Получаем текущее значение из столбца I в соответствующей строке
                    current_count = int(bot_sheet.cell(i + 2, column_percent_approved_posts).value or 0)
                    new_value = current_count + 1

                    # Обновляем ячейку в столбце I
                    bot_sheet.update_cell(i + 2, column_percent_approved_posts, new_value)

                    break
        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при суммировании одобренного поста: {e}\n{traceback.format_exc()}")

    def inactive_user(self, user_id: int, chat_id: int = 2):
        """Проверка на неактив у пользователя"""
        try:
            self._rate_limit()
            main_stats_sheet = self._get_sheet("Статистика")

            column_m = main_stats_sheet.col_values(10)[1:]  # 13 — это индекс столбца M

            for i, value in enumerate(column_m):
                if value.strip() == "":
                    continue

                if str(user_id) == str(value):

                    current_count = (main_stats_sheet.cell(i + 1, 11).value or "").lower()
                    if current_count == "неактив":
                        return True
                    else:
                        return False
        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении информации о неактиве у пользователя: {e}\n{traceback.format_exc()}")

    def reset_redactors_statistics(self, chat_id: int):
        """Обнуление статистики (/r)"""
        try:
            self._rate_limit()
            bot_sheet = self._get_sheet("Информация для бота")
            redactors_work_sheet = self._get_sheet("Работа")
            stability = self._get_sheet("Стабильность")

            bot_sheet.update_acell("B33", datetime.now().strftime("%d.%m.%Y"))

            bot_sheet.batch_clear(["B2:C25"])
            redactors_work_sheet.batch_clear(["A2:E"])
            redactors_work_sheet.batch_clear(["G2:G"])
            stability.batch_clear(["C2:AF"])

            general_func.sender(chat_id, "Статистика обнулена")
        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при сбросе статистики: {e}\n{traceback.format_exc()}")

    def info_posts_per_month(self, chat_id: int):
        try:
            self._rate_limit()
            bot_sheet = self._get_sheet("Информация для бота")

            percent_public_posts = bot_sheet.acell("B31").value
            days_since_reset_stats = bot_sheet.acell("B32").value
            date_reset_stats = bot_sheet.acell("B33").value
            posts_public_now = bot_sheet.acell("B34").value
            all_posts_public = bot_sheet.acell("B30").value
            photo_mat = bot_sheet.acell("B28").value
            video_mat = bot_sheet.acell("B29").value

            general_func.sender(chat_id, f"Количество опубликованных постов за следующее количество дней: {days_since_reset_stats}, с момента последнего сброса статистики ({date_reset_stats}) — {posts_public_now} из {all_posts_public} ({percent_public_posts}%)\n\nФотоматериал: {photo_mat}\nВидеоматериал: {video_mat}")
        except Exception as e:
            general_func.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении информации постов за месяц: {e}\n{traceback.format_exc()}")

google_sheets = GoogleSheets()