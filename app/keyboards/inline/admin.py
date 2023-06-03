from app.keyboards.inline.base import *


def event_kb(url: str):
    return InlineKeyboardMarkup(row_width=1,
                                inline_keyboard=[[InlineKeyboardButton('Відповісти клієнту', url=url)]])