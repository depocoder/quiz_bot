import os
import random
import json
import time
import logging
from dotenv import load_dotenv
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import redis
from requests.exceptions import ConnectionError
from quiz import parse_quiz


logger = logging.getLogger(__name__)
QUIZ = parse_quiz()


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)
    return keyboard


def create_question(event, vk_api, keyboard, redis_conn):
    question, answer = random.choice(list(QUIZ.items()))
    redis_conn.set(f"vk-{event.user_id}", json.dumps([question, answer]))
    reply_to_user(event, vk_api, keyboard, message=question)


def reply_to_user(event, vk_api, keyboard, message):
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message)


def check_answer(event, vk_api, keyboard, user_message,
                 question_and_answer, redis_conn):
    question, answer = json.loads(question_and_answer)
    short_answer = answer[answer.find('\n')+1:answer.find('.')]
    if user_message == 'Новый вопрос':
        reply_to_user(
            event, vk_api, keyboard,
            message=f'Вы не ответили на старый вопрос!\n{question}')
    elif user_message == 'Сдаться':
        reply_to_user(
            event, vk_api, keyboard, message=f'Правильный {answer}')
        redis_conn.delete(f"vk-{event.user_id}")
    elif user_message in short_answer and len(user_message) >= (len(short_answer)-3):
        reply_to_user(
            event, vk_api, keyboard, message=f'Верно! {answer}')
        redis_conn.delete(f"vk-{event.user_id}")
    else:
        reply_to_user(
            event, vk_api, keyboard,
            message='Я не понял команду или ответ неверный.')


def process_message(event, vk_api, redis_conn):
    user_message = event.text
    keyboard = create_keyboard()
    question_and_answer = redis_conn.get(f"vk-{event.user_id}")
    if user_message in ['Здравствуйте', 'Приветствую', 'Привет', 'Ку']:
        reply_to_user(
            event, vk_api, keyboard,
            message=('Приветствуем вас в нашей викторине!',
                     'Чтобы получить вопрос нажмите кнопку <Новый вопрос>'))
    elif not question_and_answer:
        if user_message == 'Новый вопрос' or user_message == 'Сдаться':
            create_question(event, vk_api, keyboard, redis_conn)
        else:
            reply_to_user(
                event, vk_api, keyboard,
                message='Я не понял команду или ответ неверный.')
    else:
        check_answer(
            event, vk_api, keyboard,
            user_message, question_and_answer, redis_conn)


if __name__ == "__main__":
    load_dotenv()
    redis_conn = redis.Redis(host=os.getenv('REDIS_HOST'), password=os.getenv(
        'REDIS_PASSWORD'), port=os.getenv('REDIS_PORT'), db=0)
    while True:
        try:
            vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    process_message(event, vk_api, redis_conn)
        except ConnectionError:
            logging.exception('ConnectionError - перезапуск через 30 секунд')
            time.sleep(30)
            continue
        except Exception as E:
            logging.exception(E)
