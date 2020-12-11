import logging
from functools import partial
import os
import json
import random

from dotenv import load_dotenv
import redis
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
    ConversationHandler)

from quiz import parse_quiz


logger = logging.getLogger(__name__)
SEND_QUESTION, CHECK_ANSWER = range(2)
QUIZ = parse_quiz()


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Приветствую!', reply_markup=reply_markup)
    return SEND_QUESTION


def send_question(redis_conn, update: Update, context: CallbackContext):
    question, answer = random.choice(list(QUIZ.items()))
    redis_conn.set(
        f"tg-{update.effective_user.id}", json.dumps([question, answer]))
    update.message.reply_text(question)
    return CHECK_ANSWER


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Пока. Хорошего вам дня!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def error_handler(update: Update, context: CallbackContext):
    logger.error(
        msg="Exception while handling an update:", exc_info=context.error)


def check_answer(redis_conn, update: Update, context: CallbackContext):
    user_message = update.message.text
    question_and_answer = redis_conn.get(f"tg-{update.effective_user.id}")
    question, answer = json.loads(question_and_answer)
    short_answer = answer[answer.find('\n')+1:answer.find('.')]
    if user_message == 'Новый вопрос':
        update.message.reply_text(
            f'Вы не ответили на старый вопрос!\n{question}')
    elif user_message == 'Сдаться':
        update.message.reply_text(f'Правильный {answer}')
        return SEND_QUESTION
    elif user_message in short_answer and len(user_message) >= (len(short_answer)-3):
        update.message.reply_text(f"Верно! {answer}")
        return SEND_QUESTION
    else:
        update.message.reply_text(
            "Ответ неверный! Попробуйте еще раз или сдайтесь!")


if __name__ == '__main__':
    load_dotenv()
    redis_conn = redis.Redis(
        host=os.getenv('REDIS_HOST'), password=os.getenv('REDIS_PASSWORD'),
        port=os.getenv('REDIS_PORT'), db=0)
    p_send_question = partial(send_question, redis_conn)
    p_check_answer = partial(check_answer, redis_conn)
    updater = Updater(token=os.getenv("TG_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SEND_QUESTION: [
                MessageHandler(Filters.regex('^(Новый вопрос|Сдаться)$'),
                               p_send_question)],

            CHECK_ANSWER: [MessageHandler(Filters.text, p_check_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()

    updater.idle()
