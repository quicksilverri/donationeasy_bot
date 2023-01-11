import pandas as pd 
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)

from constants import *

get_link = lambda x: f'https://docs.google.com/spreadsheets/d/{x}/export?format=csv'

class Question: 
    def __init__(self, data: pd.Series): 
        # self.number = data['number']
        self.pos = data['pos_callback']
        self.neg = data['neg_callback']
        self.ns = data['ns_callback']
        self.text = data['question_text']
        self.ns_text = data['ns_text']
        self.rejection = data['rejection_text']

    def get_reply_markup(self): 
        if self.ns != 'NONE': 
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Да', callback_data=self.pos)], 
                [InlineKeyboardButton(text='Нет', callback_data=self.neg)], 
                [InlineKeyboardButton(text='Я не уверен(a)', callback_data=self.ns)]
            ])

        else: 
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Да', callback_data=self.pos)], 
                [InlineKeyboardButton(text='Нет', callback_data=self.neg)], 
            ])

        return keyboard 


class Quiz: 
    def __init__(self, link: str):
        self.data: pd.DataFrame = pd.read_csv(get_link(link))
        self.question_list: list = self.parse_questions()
        self.length = len(self.question_list)
        self.current_question = 0

    def parse_questions(self):
        length: int = self.data.shape[0]
        questions: list = []

        for i in range(length): 
            question_series: pd.Series = self.data.iloc[i]
            question = Question(question_series)
            questions.append(question)

        return questions 

    def get_question(self): 
        question = self.question_list[self.current_question]
        self.current_question += 1

        return question


class TextManager: 
    def __init__(self, link: str, if_article: bool = False):
        self.data: pd.DataFrame = pd.read_csv(get_link(link))
        self.texts: dict = self.parse('text')

        if if_article: 
            self.titles: dict = self.parse('title')

    def parse(self, attribute): 
        length: int = self.data.shape[0]
        parsed_properties: dict = {}

        for i in range(length): 
            text_series = self.data.iloc[i]
            parsed_properties[text_series['id']] = text_series[attribute]

        return parsed_properties 

    def get_text(self, id: str): 
        return self.texts[id]

    def get_title(self, id: str): 
        return self.titles[id]

    def get_reply_markup(self): 
        buttons = [[InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]]
        for callback, title in self.titles.items(): 
            new_button = InlineKeyboardButton(text=title, callback_data=callback)
            buttons = [[new_button]] + buttons

        keyboard = InlineKeyboardMarkup(buttons)

        return keyboard


lib = TextManager(TEXT_SHEET, if_article=False)
articles = TextManager(ARTICLE_SHEET, if_article=True)
