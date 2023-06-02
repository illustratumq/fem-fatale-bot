from app.keyboards.reply.base import *


def menu_kb(authorized: bool = True):

    keyboard = [
        [KeyboardButton(Buttons.menu.news)],
        [KeyboardButton(Buttons.menu.partners), KeyboardButton(Buttons.menu.card)],
        [KeyboardButton(Buttons.menu.cashback), KeyboardButton(Buttons.menu.reserv)],
        [KeyboardButton(Buttons.menu.about), KeyboardButton(Buttons.menu.help)]
    ]

    if not authorized:
        keyboard[0].insert(0, KeyboardButton(Buttons.menu.auth))

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def introduction_kb():
    keyboard = [
        [KeyboardButton(Buttons.menu.introduction)]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def share_phone_kb():
    keyboard = [
        [KeyboardButton(Buttons.menu.phone, request_contact=True)],
        [KeyboardButton(Buttons.menu.skip)]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)