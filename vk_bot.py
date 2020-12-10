# -*- coding: utf-8 -*-
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id



def create_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    return keyboard


def main():
    vk_session = vk_api.VkApi(token='108fa3cc5ac6077a91cb5a97c1c760105e99617cde2ccd757e0def491ce9568c9c810afc4e5c4024d32bc')
    vk = vk_session.get_api()
    keyboard = create_keyboard()
    

    vk.messages.send(
        peer_id=182467266,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Пример клавиатуры'
    )


if __name__ == '__main__':
    main()