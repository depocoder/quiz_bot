# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
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
    load_dotenv()
    vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
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