from src.api.google_sheets.statistics import Statistics


class StatisticsModel:
    @staticmethod
    def redactors_statistics(msg, chat_id):
        Statistics.redactors_statistics(msg, chat_id)

    @staticmethod
    def redactors_statistics_for_admins(chat_id):
        Statistics.redactors_statistics_for_admins(chat_id)

    @staticmethod
    def reset_stats(chat_id):
        """Обнуление статистики редакторов"""
        Statistics.reset_redactors_statistics(chat_id)