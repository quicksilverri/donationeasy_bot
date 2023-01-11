from telegram.ext import (
    Updater, 
    ConversationHandler,
    CallbackContext, 
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from telegram.update import Update
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)

import logging

from constants import *
from content import Quiz, lib, articles

import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#constants
START, MENU, QUIZ, FEEDBACK, TEXT_FB, END = range(6)
START_QUIZ, QUESTION, RESULT, END_QUIZ = range(100, 104)
ARTICLE_MENU, ARTICLE = range(200, 202)
IN_DEV = 1000


def update_message(update: Update, context: CallbackContext, new_text: str, new_markup: InlineKeyboardMarkup): 
    context.bot.edit_message_text(
        text=new_text, 
        chat_id=update.effective_chat.id, 
        message_id=update.effective_message.message_id,
    )

    context.bot.edit_message_reply_markup(
        reply_markup=new_markup, 
        chat_id=update.effective_chat.id, 
        message_id=update.effective_message.message_id,
    )


def start(update: Update, context: CallbackContext): 
    text = lib.get_text('start')

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton('Перейти в меню', callback_data='menu')]]
    ) 

    context.bot.send_message(
        text=text, 
        reply_markup=keyboard, 
        chat_id=update.effective_chat.id, 
    )

    return START


def menu(update: Update, context: CallbackContext): # more like a menu??
    text = lib.get_text('menu')

    keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Пройти тест',
            callback_data='quiz')],
            [InlineKeyboardButton(text='Посмотреть статьи', 
            callback_data='articles')], 
            [InlineKeyboardButton('Закрыть бота', callback_data='end')]
        ]
    )

    update_message(update, context, text, keyboard)

    logger.info('Menu opened successfully')

    return MENU

def in_development(update: Update, context: CallbackContext): 
    text = lib.get_text('in_development')

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Вернуться в меню', 
        callback_data='menu')]]
    )

    update_message(update, context, text, keyboard)

    return START


def start_quiz(update: Update, context: CallbackContext): 
    user = context.user_data
    user['quiz'] = Quiz(QUIZ_SHEET)

    text = lib.get_text('start_quiz')

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text='K первому вопросу!', callback_data='next')
    ]])
    
    update_message(update, context, text, keyboard)

    return QUESTION

def ask_question(update: Update, context: CallbackContext): 
    quiz = context.user_data['quiz']
    question = quiz.get_question()
    text = question.text
    keyboard = question.get_reply_markup()

    update_message(update, context, text, keyboard)

    context.user_data['current_question'] = question
    return QUESTION

def approve_donation(update: Update, context: CallbackContext): 
    text = lib.get_text('approve_donation')
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text='Завершить опросник', callback_data='end_quiz')
    ]])

    update_message(update, context, text, keyboard)

    return RESULT

def reject_donation(update: Update, context: CallbackContext): 
    question = context.user_data['current_question']
    text = question.rejection
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text='Завершить опросник', callback_data='end_quiz')
    ]])

    update_message(update, context, text, keyboard)
    return RESULT

def end_quiz(update: Update, context: CallbackContext):
    text = lib.get_text('end_quiz')
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    ]])

    update_message(update, context, text, keyboard)
    return END_QUIZ


def show_articles_menu(update: Update, context: CallbackContext): 
    text = lib.get_text('article_menu')
    keyboard = articles.get_reply_markup()
    # keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text='meow', callback_data='a11')]])

    update_message(update, context, text, keyboard)
    logger.info('Article menu is here \n\n')
    return ARTICLE_MENU


def show_article(update: Update, context: CallbackContext): 
    article_id: str = update.callback_query.data
    logger.info(article_id)

    text = articles.get_text(article_id)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text='Вернуться к выбору статьи', callback_data='article_menu')
    ]])

    update_message(update, context, text, keyboard)
    return ARTICLE


def end(update: Update, context: CallbackContext):
    text = lib.get_text('end')

    context.bot.send_message(
        text=text, 
        chat_id=update.effective_chat.id,
    ) 

    logger.info('End executed~')
    return ConversationHandler.END


def main(): 
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    article_pattern = re.compile('a[0-9][0-9]')

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start), 
        ], 
        
        states={
            START: [CallbackQueryHandler(menu, pattern='menu')], 
            MENU: [
                CallbackQueryHandler(start_quiz, pattern='quiz'),
                CallbackQueryHandler(show_articles_menu, pattern='articles'),
            ], 
            QUESTION: [
                CallbackQueryHandler(ask_question, pattern='next'), 
                CallbackQueryHandler(approve_donation, pattern='can_donate'), 
                CallbackQueryHandler(reject_donation, pattern='not_allowed'), 
            ], 
            RESULT: [
                CallbackQueryHandler(end_quiz, pattern='end_quiz'), 
            ], 
            END_QUIZ: [
                CallbackQueryHandler(menu, pattern='menu')
            ],
            ARTICLE_MENU: [
                CallbackQueryHandler(show_article, pattern=article_pattern),
                CallbackQueryHandler(menu, pattern='menu')
            ], 
            ARTICLE: [
                CallbackQueryHandler(show_articles_menu, pattern='article_menu')
            ],
        }, 

        fallbacks=[
            CallbackQueryHandler(end, pattern='end'), 
            CommandHandler('end', end)
        ]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
