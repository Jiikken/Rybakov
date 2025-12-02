import logging
import traceback
from datetime import datetime
from typing import Optional

from src.services.models.senders import Senders
from src.api.google_sheets.init import GoogleSheets


class Statistics(GoogleSheets):
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
                        Senders.sender(chat_id, f"Информации за этот период ещё нет (максимум дней: {days_since_restart})")
                        return
                    if select_days < 0:
                        Senders.sender(chat_id, f"Не могу показать информацию за минусовой период")
                        return
                except ValueError:
                    Senders.sender(chat_id, "Не могу отправить статистику за данный период")
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

            Senders.sender(chat_id, statistics)

        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
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

            Senders.sender(chat_id, statistics)
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении статистики редакторов для администрации: {e}\n{traceback.format_exc()}")

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

            Senders.sender(chat_id, "Статистика обнулена")
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при сбросе статистики: {e}\n{traceback.format_exc()}")

statistics_from_gs = Statistics()