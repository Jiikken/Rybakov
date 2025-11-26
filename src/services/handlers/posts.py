import json
import time
import traceback

from vk_api.bot_longpoll import VkBotEventType

from api.vk.vk import VkConnection
from src.database.operations.posts import Posts as PostsDataBase
from src.api.google_sheets.posts import Posts as PostsGoogleSheets
from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.general_functions import general_func
from src.utils.keyboards import create_buttons, create_buttons_ls, cheburek
from src.utils.logs import logging
from vk_api.upload import VkUpload


class HandlerCommandsForPostsInChat:
    def __init__(self):
        self.commands_for_posts = {
            "#одобрено": {
                "handler": self._approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg"]
            },
            "#oдобрено": {
                "handler": self._approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg"]
            },
            "#несмешно": {
                "handler": self._no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type1"]
            },
            "#неcмешно": {
                "handler": self._no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type1"]
            },
            "#плагиат": {
                "handler": self._no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type2"]
            },
            "#плaгиат": {
                "handler": self._no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type2"]
            },
            "#непрезентабельно": {
                "handler": self._no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type3"]
            },
            "#нeпрезентабельно": {
                "handler": self._no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type3"]
            },
            "#персональный ответ": {
                "handler": self._personal_response_for_chat,
                "admin_only": True,
                "params": ["user_id", "chat_id", "msg"]
            },
            "#пeрсональный ответ": {
                "handler": self._personal_response_for_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "user_id"]
            },
            "#мем": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#видео": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#клип": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#mem": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#video": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#clip": {
                "handler": self._enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            }
        }

    def handler_commands_for_posts(self, msg, user_id, chat_id, event):
        forward_message = None

        for cmd in self.commands_for_posts:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        if forward_message:
            command = self.commands_for_posts.get(forward_message)

            if command["admin_only"] and chat_id == 1:
                params = {}

                for param in command["params"]:
                    if param == "chat_id":
                        params["chat_id"] = chat_id
                    elif param == "msg":
                        params["msg"] = msg
                    elif param == "user_id":
                        params["user_id"] = user_id
                    elif param == "event":
                        params["event"] = event
                    elif param == "type1":
                        params["type"] = 1
                    elif param == "type2":
                        params["type"] = 2
                    elif param == "type3":
                        params["type"] = 3

                try:
                    command["handler"](**params)
                except Exception as e:
                    general_func.sender(chat_id, f"Произошла ошибка при выполнении команды")
                    logging.error(f"Ошибка в команде {msg}: {e}\n{traceback.format_exc()}")

            elif not command["admin_only"] and chat_id == 5:
                try:
                    self._enter_post(chat_id, user_id, event)
                except Exception as e:
                    general_func.sender(chat_id, f"Произошла ошибка при выполнении команды")
                    logging.error(f"Произошла ошибка при отправке поста на проверку: {e}\n{traceback.format_exc()}")

            elif not command["admin_only"] and chat_id != 5:
                general_func.sender(chat_id, f"Данное действие недоступно в текущей беседе")

    @staticmethod
    def _approved_post_chat(chat_id, msg, content_chat = 5, bank_content = 4):
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
                        PostsDataBase.change_posts_inspection(False, chat_id)
                    if posts > 0:
                        PostsDataBase.change_approved_posts(chat_id, True)

                user_id = PostAndUser.get_user_by_post(message_id, chat_id)
                PostsGoogleSheets.summ_approved_posts(user_id, chat_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                general_func.sender(content_chat,
                       f"Пост #{message_id} был одобрен!\n\nВ ближайшее время он будет опубликован",
                       f"{general_func.get_midd(msg, chat_id)}")
                general_func.sender(bank_content, f'', f"{general_func.get_midd(msg, chat_id)}")

        else:
            general_func.sender(chat_id, "Номер поста должен быть больше нуля")

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
    def _no_approved_post_chat(chat_id, msg, type, content_chat = 5):
        message_id = general_func.get_post_id_from_message(chat_id, msg)

        if message_id > 0:
            if str(message_id) not in PostsDataBase.get_no_check_posts_list():
                general_func.sender(chat_id, f"Пост #{message_id} уже проверен")

            else:
                general_func.sender(chat_id, f"Пост #{message_id} был отказан")
                posts_inspection = PostsDataBase.get_posts_info()[2]

                if posts_inspection > 0:
                    PostsDataBase.change_posts_inspection(False, chat_id)

                PostAndUser.remove_post_to_user(message_id, chat_id)
                PostsDataBase.remove_post_from_db(message_id, chat_id)

                if type == 1:
                    general_func.sender(content_chat,
                           f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: материал не выглядит юмористическим. Возможно, стоит доработать идеи или подойти с другой стороны",
                           f"{general_func.get_midd(msg, chat_id)}")
                elif type == 2:
                    general_func.sender(content_chat,
                           f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, Ваш материал отклонён, так как в нём обнаружен плагиат",
                           f"{general_func.get_midd(msg, chat_id)}")
                elif type == 3:
                    general_func.sender(content_chat,
                           f"Пост #{general_func.get_post_id_from_message(chat_id, msg)} был отклонен по следующей причине причине: к сожалению, мы не можем принять этот материал, так как он не соответствует требованиям к презентабельности",
                           f"{general_func.get_midd(msg, chat_id)}")

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

    def _personal_response_for_chat(self, chat_id, msg, user_id, content_chat = 5):
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
                    general_func.sender(chat_id, f"Персональный ответ на пост #{message_id} был отправлен")
                    posts_inspection = PostsDataBase.get_posts_info()[2]

                    if posts_inspection > 0:
                        PostsDataBase.change_posts_inspection(False, chat_id)

                    midd = json.dumps(
                        {"peer_id": 2000000000 + content_chat, "conversation_message_ids": message_id,
                         "is_reply": False})
                    general_func.sender(content_chat, f"Проверяющий дал персональный ответ на пост #{message_id}: {response}",
                           f"{midd}")

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

    @staticmethod
    def _enter_post(chat_id, user_id, event, content_chat = 5, admin_chat = 1):
        if PostsGoogleSheets.inactive_user(user_id, chat_id):
            general_func.sender(chat_id,
                   "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            message_id = event.message.get("conversation_message_id")
            midd = json.dumps(
                {"peer_id": 2000000000 + content_chat, "conversation_message_ids": message_id, "is_reply": False})
            general_func.sender(chat_id, f"Пост отправлен на рассмотрение под номером #{message_id}", midd)

            PostAndUser.add_post_to_user(message_id, user_id, chat_id)

            PostsGoogleSheets.summ_posts(user_id, chat_id)
            PostsDataBase.add_post_to_db(message_id, chat_id)

            PostsDataBase.change_posts_inspection(True, chat_id)
            PostsDataBase.change_posts(True, chat_id)

            general_func.sender(admin_chat, f"Внимание! Новая идея для поста #{message_id}", midd, keyboard=create_buttons(message_id))

    @staticmethod
    def _wait_for_user_input(chat_id, message_id, timeout=60):
        """Для персонального ответа"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            for event in VkConnection.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat and event.chat_id == chat_id:
                        user_id = event.message.get("from_id")
                        if user_id == PostAndUser.get_admin_id_by_response_post(message_id):
                            user_response = event.object.message['text']
                            return user_response

        general_func.sender(chat_id, 'Время ожидания истекло')
        return None

class HandlerCommandsForPostsInLS:
    def __init__(self):
        self.commands_for_posts = {
            "#мем": {
                "handler": self._handle_enter_post_in_ls
            },
            "#видео": {
                "handler": self._handle_enter_post_in_ls
            },
            "#клип": {
                "handler": self._handle_enter_post_in_ls
            },
            "#mem": {
                "handler": self._handle_enter_post_in_ls
            },
            "#video": {
                "handler": self._handle_enter_post_in_ls
            },
            "#clip": {
                "handler": self._handle_enter_post_in_ls
            }
        }

    def handler_ls_messages(self, msg, user_id, event):
        forward_message = None

        for cmd in self.commands_for_posts:
            if cmd.lower() in msg.lower():
                forward_message = cmd

        if forward_message:
            command = self.commands_for_posts.get(forward_message)

            try:
                command["handler"](user_id, event)
            except Exception as e:
                general_func.sender_in_ls(user_id, f"Произошла ошибка при обращении к методу")
                logging.error(f"Ошибка при выполнении команды {forward_message}: {e}\n{traceback.format_exc()}")
        elif msg.lower() == "хочу":
            self.send_cheburek(user_id)
        elif msg.lower() == "пельмень":
            self.send_dikiy_ogyrec(user_id)
        else:
            general_func.sender_in_ls(user_id, f"Здравствуйте, {general_func.info_user(user_id)}\n\nХотите чебурек?", keyboard=cheburek())

    @staticmethod
    def _handle_enter_post_in_ls(user_id, event, admin_chat = 1):
        """Отправка поста на проверку в ЛС"""
        if PostsGoogleSheets.inactive_user(user_id):
            general_func.sender_in_ls(user_id,
                         "На данный момент, я не могу рассмотреть от Вас материал, так как Вы находитесь в неактиве")
        else:
            user_id = event.message.get("from_id")
            message_id = event.message.get("id")

            general_func.sender_in_ls(user_id, f"Пост отправлен на рассмотрение под номером #{message_id}", message_id)

            PostAndUser.add_post_to_user(message_id, user_id)

            PostsGoogleSheets.summ_posts(user_id)
            PostsDataBase.add_post_to_db(message_id)

            PostsDataBase.change_posts_inspection(True)
            PostsDataBase.change_posts(True)

            general_func.resend_in_ls(admin_chat, f"Внимание! Новая идея для поста #{message_id}", message_id,
                         keyboard=create_buttons_ls(message_id))

    @staticmethod
    def send_cheburek(user_id):
        """Отправляет загруженное фото чебурека"""
        try:
            # Загружаем фото на сервер ВК
            cheburk = "Rybakov/src/photos/чебурек.jpg"
            photo = VkUpload(VkConnection.vk_session).photo_messages(cheburk)[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"

            # Отправляем сообщение с фото
            general_func.sender_in_ls(user_id, "Держите чебурек🥟", attachment=attachment)
        except Exception as e:
            general_func.sender_in_ls(user_id, "Чебуреки кончились😢")
            logging.warning(f"Чебурек: {e}\n{traceback.format_exc()}")

    @staticmethod
    def send_dikiy_ogyrec(user_id):
        """Отправляет загруженное фото чебурека"""
        try:
            # Загружаем фото на сервер ВК
            cheburk = "Rybakov/src/photos/дикий огурец.jpg"
            photo = VkUpload(VkConnection.vk_session).photo_messages(cheburk)[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"

            # Отправляем сообщение с фото
            general_func.sender_in_ls(user_id, "😱", attachment=attachment)
        except Exception as e:
            general_func.sender_in_ls(user_id, "😢")
            logging.warning(f"Дикий огурец: {e}\n{traceback.format_exc()}")
