from src.database.operations.posts import Posts as PostsDataBase
from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.models.senders import Senders
from src.services.models.posts import Posts


class CommandsModelLS:
    @staticmethod
    def approved_post_ls(chat_id, msg, bank_content = 4):
        message_id = Posts.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                Senders.sender(chat_id, f"Пост #{message_id} был одобрен")

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

                Senders.sender_in_ls(user_id,
                             f"Пост #{message_id} был одобрен!\n\nВ ближайшее время он будет опубликован",
                             message_id)
                Senders.resend_in_ls(bank_content, f'', message_id)

        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    @staticmethod
    def no_approved_post_ls(chat_id, msg, type):
        message_id = Posts.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            else:
                Senders.sender(chat_id, f"Пост #{message_id} был отказан")
                posts_inspection = PostsDataBase.get_posts_info()[2]

                if posts_inspection > 0:
                    PostsDataBase.change_posts_inspection(False)

                user_id = PostAndUser.get_user_by_post(message_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                if type == 1:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{Posts.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: материал не выглядит юмористическим. Возможно, стоит доработать идеи или подойти с другой стороны",
                                 f"{Posts.get_post_id_from_message(chat_id, msg)}")
                elif type == 2:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{Posts.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, Ваш материал отклонён, так как в нём обнаружен плагиат",
                                 f"{Posts.get_post_id_from_message(chat_id, msg)}")
                elif type == 3:
                    Senders.sender_in_ls(user_id,
                                 f"Пост #{Posts.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, мы не можем принять этот материал, так как он не соответствует требованиям к презентабельности",
                                 f"{Posts.get_post_id_from_message(chat_id, msg)}")

        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    def personal_response_for_ls(self, chat_id, msg, user_id):
        message_id = Posts.get_post_id_from_message_for_personal_response(chat_id, msg)
        PostAndUser.add_personal_response_to_post(message_id, user_id)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                Senders.sender(chat_id, f"Пост #{message_id} уже проверен")

            elif message_id:
                Senders.sender(chat_id, 'Пожалуйста, введите текст для персонального ответа, с маленькой буквы')
                response = self.wait_for_user_input(chat_id, message_id)
                PostAndUser.remove_personal_response_to_post(message_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                if response:
                    Senders.sender(chat_id, f'Персональный ответ на пост #{message_id} был отправлен')
                    posts_inspection = PostsDataBase.get_posts_info()[2]

                    if posts_inspection > 0:
                        PostsDataBase.change_posts_inspection(False)

                    user_id = PostAndUser.get_user_by_post(message_id)

                    Senders.sender_in_ls(user_id,
                                 f"Проверяющий дал персональный ответ на пост #{message_id}: {response}",
                                 message_id)
        else:
            Senders.sender(chat_id, "Номер поста должен быть больше нуля")

    