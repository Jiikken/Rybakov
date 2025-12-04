import logging
import traceback

from src.services.models.senders import Senders
from src.api.google_sheets.google_sheets import GoogleSheets


class Posts(GoogleSheets):
    def summ_posts(self, user_id: int, chat_id: int = 2):
        """Метод для статистики количества постов отправленных от пользователя"""
        try:
            self.rate_limit()
            sheets = self.manager.sheets
            redactors = self.manager.redactors_info
            days = self.manager.days

            redactors_ids = redactors.ids
            day_reset_stats = days.day_reset_stats
            days_reset_stats = days.days_reset_stats

            for index, redactor_id in enumerate(redactors_ids):
                redactor_id = redactor_id.strip()

                if redactor_id.isdigit():
                    if str(user_id) == str(redactor_id):
                        for i in days_reset_stats:
                            if day_reset_stats.value == i:
                                current_count = int(sheets.stability.cell(index + 2, int(i) + 2).value)
                                new_value = current_count + 1

                                sheets.stability.update_cell(index + 2, int(i) + 2, new_value)

        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при суммировании поста: {e}\n{traceback.format_exc()}")

    def summ_approved_posts(self, user_id: int, chat_id: int):
        try:
            self.rate_limit()
            sheets = self.manager.sheets
            redactors = self.manager.redactors_info

            redactors_ids = redactors.ids
            approved_posts = int(redactors.approved_posts + 1)

            for i, value in enumerate(redactors_ids):
                if str(user_id) == str(value):

                    # Получаем текущее значение из столбца I в соответствующей строке
                    current_count = int(sheets.bot_sheet.cell(i + 2, approved_posts).value or 0)
                    new_value = current_count + 1

                    # Обновляем ячейку в столбце I
                    sheets.bot_sheet.update_cell(i + 2, approved_posts, new_value)

                    break
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при суммировании одобренного поста: {e}\n{traceback.format_exc()}")

    def info_posts_per_month(self, chat_id: int):
        try:
            self.rate_limit()
            sheets = self.manager.sheets
            days = self.manager.days

            percent_public_posts = sheets["bot_sheet"].acell("B31").value
            days_since_reset_stats = days.days_since_reset_stats
            date_reset_stats = days.date_reset_stats
            posts_public_now = sheets["bot_sheet"].acell("B34").value
            all_posts_public = sheets["bot_sheet"].acell("B30").value
            photo_mat = sheets["bot_sheet"].acell("B28").value
            video_mat = sheets["bot_sheet"].acell("B29").value

            Senders.sender(chat_id, f"Количество опубликованных постов за следующее количество дней: {days_since_reset_stats}, с момента последнего сброса статистики ({date_reset_stats}) — {posts_public_now} из {all_posts_public} ({percent_public_posts}%)\n\nФотоматериал: {photo_mat}\nВидеоматериал: {video_mat}")
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении информации постов за месяц: {e}\n{traceback.format_exc()}")

    def inactive_user(self, user_id: int, chat_id: int = 2) -> bool:
        """Проверка на неактив у пользователя"""
        try:
            self.rate_limit()
            sheets = self.manager.sheets
            redactors = self.manager.redactors_info

            redactors_ids = redactors.ids

            for i, value in enumerate(redactors_ids):
                if value.strip() == "":
                    continue

                if str(user_id) == str(value):

                    current_count = (sheets.stats.cell(i + 1, 11).value or "").lower()
                    if current_count == "неактив":
                        return True
                    else:
                        return False
        except Exception as e:
            Senders.sender(chat_id, f"Произошла ошибка при обращении к методу")
            logging.error(f"Ошибка при получении информации о неактиве у пользователя: {e}\n{traceback.format_exc()}")

posts_google_sheets = Posts()