import pandas as pd 
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)

from constants import *


class Question: 
    def __init__(self, data: pd.Series): 
        self.number = data['number']
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
    def __init__(self, link: str):
        self.data: pd.DataFrame = pd.read_csv(get_link(link))
        self.texts = self.parse_texts()


    def parse_texts(self): 
        length: int = self.data.shape[0]
        texts: dict = {}

        for i in range(length): 
            text_series = self.data.iloc[i]
            texts[text_series['id']] = text_series['text']

        return texts 

    def get_text(self, id: str): 
        return self.texts[id]


lib = TextManager(TEXT_SHEET)
quiz = Quiz(QUIZ_SHEET)
