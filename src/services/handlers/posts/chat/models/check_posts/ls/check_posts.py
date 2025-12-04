from src.database.operations.posts import posts_data_base
from src.api.google_sheets.posts import posts_google_sheets
from src.database.operations.post_and_user import post_and_user
from src.services.models.senders import Senders
from src.services.models.posts import info_about_posts_in_chat


class CommandsModelLS:
    """

        Модели команд для проверки постов из ЛС

    """
    def approved_post_ls(self, chat_id: int, msg: str, bank_content: int = 4):
        """
        Одобрение поста

        :param chat_id: ID чата, куда прислано сообщение
        :param msg: Текст сообщения
        :param bank_content: ID чата для хранения контента, по умолчанию 4
        """
        message_id = info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in posts_data_base.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                Senders.sender(chat_id, f"Пост #{message_id} был одобрен")

                posts_inspection = posts_data_base.get_posts_info()[2]
                posts = posts_data_base.get_posts_info()[0]
                if posts_inspection:
                    if posts_inspection > 0:
                        posts_data_base.change_posts_inspection(False)
                    if posts > 0:
                        posts_data_base.change_approved_posts(chat_id, True)

                user_id = post_and_user.get_user_by_post(message_id)

                posts_google_sheets.summ_approved_posts(user_id, chat_id)

                self._user_remove_from_db(message_id, chat_id)

                Senders.sender_in_ls(user_id,
                             f"Пост #{message_id} был одобрен!\n\nВ ближайшее время он будет опубликован",
                             message_id)
                Senders.resend_from_ls(bank_content, f'', message_id)

        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    def no_approved_post_ls(self, chat_id: int, msg: str, type: int):
        """
        Отклонение поста

        :param chat_id: ID чата, куда прислано сообщение
        :param msg: Текст сообщения
        :param type: Причина по которой пост отклонён (1 - несмешно, 2 - плагиат, 3 - непрезентабельно)
        """
        message_id = info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in posts_data_base.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            else:
                Senders.sender(chat_id, f"Пост #{message_id} был отказан")
                posts_inspection = posts_data_base.get_posts_info()[2]

                if posts_inspection > 0:
                    posts_data_base.change_posts_inspection(False)

                user_id = post_and_user.get_user_by_post(message_id)

                self._user_remove_from_db(message_id, chat_id)

                if type == 1:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: материал не выглядит юмористическим. Возможно, стоит доработать идеи или подойти с другой стороны",
                                 f"{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)}")
                elif type == 2:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, Ваш материал отклонён, так как в нём обнаружен плагиат",
                                 f"{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)}")
                elif type == 3:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, мы не можем принять этот материал, так как он не соответствует требованиям к презентабельности",
                                 f"{info_about_posts_in_chat.get_post_id_from_message(chat_id, msg)}")

        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    def personal_response_for_ls(self, chat_id: int, msg: str, user_id: int):
        """
            Персональный ответ пользователю

            :param chat_id: ID чата, куда прислано сообщение
            :param msg: Текст сообщения
            :param user_id: ID пользователя, от которого пришло сообщение
        """
        message_id = info_about_posts_in_chat.get_post_id_from_message_for_personal_response(chat_id, msg)
        post_and_user.add_personal_response_to_post(message_id, user_id)

        if message_id > 0:
            if str(message_id) not in posts_data_base.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                Senders.sender(chat_id, 'Пожалуйста, введите текст для персонального ответа, с маленькой буквы')
                response = info_about_posts_in_chat.wait_for_user_input(chat_id, message_id)
                post_and_user.remove_personal_response_to_post(message_id)

                self._user_remove_from_db(message_id, chat_id)

                if response:
                    Senders.sender(chat_id, f'Персональный ответ на пост #{message_id} был отправлен')
                    posts_inspection = posts_data_base.get_posts_info()[2]

                    if posts_inspection > 0:
                        posts_data_base.change_posts_inspection(False)

                    user_id = post_and_user.get_user_by_post(message_id)

                    Senders.sender_in_ls(user_id,
                                 f"Проверяющий дал персональный ответ на пост #{message_id}: {response}",
                                 message_id)
        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    @staticmethod
    def _user_remove_from_db(message_id: int, chat_id: int):
        """
        Удаление связи пользователя с базой данных

        :param message_id: ID сообщения
        :param chat_id: ID чата куда отправлено сообщение
        """
        post_and_user.remove_post_to_user(message_id, chat_id)
        posts_data_base.remove_post_from_db(message_id, chat_id)