from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Keyboards:
    @staticmethod
    def create_buttons(mid: int) -> VkKeyboard:
        """
        Клавиатура для проверки постов из беседы

        :param mid: ID поста
        :return: VkKeyboard
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"#Одобрено {mid}", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"#Несмешно {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f"#Плагиат {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label=f"#Непрезентабельно {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f'#Персональный ответ {mid}', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()
    
    @staticmethod
    def create_buttons_ls(mid: int) -> VkKeyboard:
        """
        Клавиатура для проверки постов из ЛС

        :param mid: ID поста
        :return: VkKeyboard
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"#Oдобрено {mid}", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"#Неcмешно {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f"#Плaгиат {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label=f"#Нeпрезентабельно {mid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f'#Пeрсональный ответ {mid}', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()
    
    @staticmethod
    def cheburek() -> VkKeyboard:
        """
        Клавиатура для выбора между огурцом и чебуреком

        :return: VkKeyboard
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"Хочу", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"Пельмень", color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()
    