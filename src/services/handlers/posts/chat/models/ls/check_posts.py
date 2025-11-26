from src.database.operations.posts import Posts as PostsDataBase
from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.general_functions import general_func


class CommandsModelLS:
    @staticmethod
    def _approved_post_ls(chat_id, msg, bank_content = 4):
        message_id = general_func.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                general_func.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                general_func.sender(chat_id, f"Пост #{message_id} был одобрен")

                posts_inspection = PostsDataBase.get_posts_info()[2]
                posts = PostsDataBase.get_posts_info()[0]
                if posts_inspection:
                    if posts_inspection > 0:
                        PostsDataBase.change_posts_inspection(False)
                    if posts > 0:
                        PostsDataBase.change_approved_posts(chat_id, True)

                user_id = PostAndUser.get_user_by_post(message_id)

                PostsGoogleSheets.summ_approved_posts(user_id, chat_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                general_func.sender_in_ls(user_id,
                             f"Пост #{message_id} был одобрен!\n\nВ ближайшее время он будет опубликован",
                             message_id)
                general_func.resend_in_ls(bank_content, f'', message_id)

        else:
            general_func.sender(chat_id, "Номер поста должен быть больше нуля")

    @staticmethod
    def _no_approved_post_ls(chat_id, msg, type):
        message_id = general_func.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                general_func.sender(chat_id, f"Пост #{message_id} уже проверен")

            else:
                general_func.sender(chat_id, f"Пост #{message_id} был отказан")
                posts_inspection = PostsDataBase.get_posts_info()[2]

                if posts_inspection > 0:
                    PostsDataBase.change_posts_inspection(False)

                user_id = PostAndUser.get_user_by_post(message_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                if type == 1:
                    general_func.sender_in_ls(user_id,
                                 f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: материал не выглядит юмористическим. Возможно, стоит доработать идеи или подойти с другой стороны",
                                 f"{general_func.get_post_id_from_message(chat_id, msg)}")
                elif type == 2:
                    general_func.sender_in_ls(user_id,
                                 f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, Ваш материал отклонён, так как в нём обнаружен плагиат",
                                 f"{general_func.get_post_id_from_message(chat_id, msg)}")
                elif type == 3:
                    general_func.sender_in_ls(user_id,
                                 f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, мы не можем принять этот материал, так как он не соответствует требованиям к презентабельности",
                                 f"{general_func.get_post_id_from_message(chat_id, msg)}")

        else:
            general_func.sender(chat_id, "Номер поста должен быть больше нуля")

    def _personal_response_for_ls(self, chat_id, msg, user_id):
        message_id = general_func.get_post_id_from_message_for_personal_response(chat_id, msg)
        PostAndUser.add_personal_response_to_post(message_id, user_id)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                general_func.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                general_func.sender(chat_id, 'Пожалуйста, введите текст для персонального ответа, с маленькой буквы')
                response = self._wait_for_user_input(chat_id, message_id)
                PostAndUser.remove_personal_response_to_post(message_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                if response:
                    general_func.sender(chat_id, f'Персональный ответ на пост #{message_id} был отправлен')
                    posts_inspection = PostsDataBase.get_posts_info()[2]

                    if posts_inspection > 0:
                        PostsDataBase.change_posts_inspection(False)

                    user_id = PostAndUser.get_user_by_post(message_id)

                    general_func.sender_in_ls(user_id,
                                 f"Проверяющий дал персональный ответ на пост #{message_id}: {response}",
                                 message_id)
        else:
            general_func.sender(chat_id, "Номер поста должен быть больше нуля")

    