import logging
import os
import json
import random
from dotenv import load_dotenv
import redis
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
    ConversationHandler)

SEND_QUESTION, CHECK_ANSWER = range(2)

load_dotenv()
r = redis.Redis(host=os.getenv('REDIS_HOST'), password=os.getenv('REDIS_PASSWORD'), port=os.getenv('REDIS_PORT'), db=0)
logger = logging.getLogger(__name__)


def parse_quiz():
    with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as my_file:
        file_contents = my_file.read()

    file_contents_splitten = file_contents.split('\n\n')
    questions = [question for question in file_contents_splitten if 'Вопрос' in question]
    answers = [answer for answer in file_contents_splitten if 'Ответ' in answer]
    return dict(zip(questions, answers))


QUIZ = parse_quiz()


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Приветствую!', reply_markup=reply_markup)
    return SEND_QUESTION


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def send_question(update: Update, context: CallbackContext) -> None:
    question, answer = random.choice(list(QUIZ.items()))
    r.set(update.effective_user.id, json.dumps([question, answer]))
    update.message.reply_text(question)
    return CHECK_ANSWER


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def check_answer(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    question_and_answer = r.get(update.effective_user.id)
    question, answer = json.loads(question_and_answer)
    short_answer = answer[answer.find('\n')+1:answer.find('.')]
    if user_message == 'Новый вопрос':
        update.message.reply_text(f'Вы не ответили на старый вопрос!\n{question}')
    elif user_message == 'Сдаться':
        update.message.reply_text(f'Правильный\n{answer}')
        return SEND_QUESTION
    elif user_message in short_answer and len(user_message) >= (len(short_answer)-1):
        update.message.reply_text(f"Верно! {answer}")
        return SEND_QUESTION
    else:
        update.message.reply_text(
            "Ответ неверный! Попробуйте еще раз или сдайтесь!")


if __name__ == '__main__':
    updater = Updater(token=os.getenv("TG_TOKEN"), use_context=True)

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SEND_QUESTION: [
                MessageHandler(Filters.regex('^(Новый вопрос|Сдаться)$'),
                               send_question)],

            CHECK_ANSWER: [MessageHandler(Filters.text, check_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()

    updater.idle()
