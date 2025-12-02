from src.api.google_sheets.statistics import statistics_from_gs


class StatisticsModel:
    @staticmethod
    def redactors_statistics(msg, chat_id):
        statistics_from_gs.redactors_statistics(msg, chat_id)

    @staticmethod
    def redactors_statistics_for_admins(chat_id):
        statistics_from_gs.redactors_statistics_for_admins(chat_id)

    @staticmethod
    def reset_stats(chat_id):
        """Обнуление статистики редакторов"""
        statistics_from_gs.reset_redactors_statistics(chat_id)