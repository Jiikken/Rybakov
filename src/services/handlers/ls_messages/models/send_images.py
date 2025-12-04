import traceback

from vk_api.upload import VkUpload

from src.api.vk.vk import VkConnection
from src.services.models.senders import Senders
from src.utils.logs import logging


class SendImagesModel:
    @staticmethod
    def send_cheburek(user_id: int):
        """
        Отправляет загруженное фото чебурека

        :param user_id: ID пользователя, которому нужно отправить чебурек
        """
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
        """
        Отправляет загруженное фото дикого огурца

        :param user_id: ID пользователя, которому нужно отправить дикий огурец
        """
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