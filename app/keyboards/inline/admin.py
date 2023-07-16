from app.keyboards.inline.base import *


def event_kb(url: str = None, chat_url: str = None):
    inline_keyboard = [
        [InlineKeyboardButton('Чат 💬', url=chat_url)]
    ]
    if url:
        inline_keyboard.append([InlineKeyboardButton('Відповісти клієнту', url=url)])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=inline_keyboard)