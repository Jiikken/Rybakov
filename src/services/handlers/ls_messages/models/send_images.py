import traceback

from api.vk.vk import VkConnection
from src.database.operations.post_and_user import PostAndUser as PostAndUser
from src.services.models.senders import Senders
from src.utils.logs import logging
from vk_api.upload import VkUpload


class SendImagesModel:
    @staticmethod
    def send_cheburek(user_id):
        """Отправляет загруженное фото чебурека"""
        try:
            # Загружаем фото на сервер ВК
            cheburk = "Rybakov/src/photos/чебурек.jpg"
            photo = VkUpload(VkConnection.vk_session).photo_messages(cheburk)[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"

            # Отправляем сообщение с фото
            Senders.sender_in_ls(user_id, "Держите чебурек🥟", attachment=attachment)
        except Exception as e:
            Senders.sender_in_ls(user_id, "Чебуреки кончились😢")
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
            Senders.sender_in_ls(user_id, "😱", attachment=attachment)
        except Exception as e:
            Senders.sender_in_ls(user_id, "😢")
            logging.warning(f"Дикий огурец: {e}\n{traceback.format_exc()}")