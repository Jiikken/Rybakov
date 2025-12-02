from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Keyboards:
    @staticmethod
    def create_buttons(cid):
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"#Одобрено {cid}", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"#Несмешно {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f"#Плагиат {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label=f"#Непрезентабельно {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f'#Персональный ответ {cid}', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()
    
    @staticmethod
    def create_buttons_ls(cid):
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"#Oдобрено {cid}", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"#Неcмешно {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f"#Плaгиат {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label=f"#Нeпрезентабельно {cid}", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label=f'#Пeрсональный ответ {cid}', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()
    
    @staticmethod
    def cheburek():
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label=f"Хочу", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label=f"Пельмень", color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()
    