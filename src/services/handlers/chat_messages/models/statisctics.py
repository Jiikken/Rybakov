from src.api.google_sheets.statistics import statistics_from_gs


class StatisticsModel:
    @staticmethod
    def redactors_statistics(msg: str, chat_id: int):
        """
        Информация о статистике редакторов за выбранный период дней (/i)

        :param msg: Сообщение события
        :param chat_id: ID чата, где произошло событие
        """
        statistics_from_gs.redactors_statistics(msg, chat_id)

    @staticmethod
    def redactors_statistics_for_admins(chat_id: int):
        """
        Информация о подробной статистике редакторов за определённый период дней (/ai)

        :param chat_id: ID чата, где произошло событие
        """
        statistics_from_gs.redactors_statistics_for_admins(chat_id)

    @staticmethod
    def reset_stats(chat_id: int):
        """
        Обнуление статистики редакторов (/r)

        :param chat_id: ID чата, где произошло событие
        """
        statistics_from_gs.reset_redactors_statistics(chat_id)