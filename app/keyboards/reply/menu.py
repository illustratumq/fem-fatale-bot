from app.keyboards.reply.base import *


def menu_kb(authorized: bool = True, admin: bool = False):

    keyboard = [
        [KeyboardButton(Buttons.menu.news)],
        [KeyboardButton(Buttons.menu.partners), KeyboardButton(Buttons.menu.card)],
        [KeyboardButton(Buttons.menu.cashback), KeyboardButton(Buttons.menu.reserv)],
        [KeyboardButton(Buttons.menu.about), KeyboardButton(Buttons.menu.help)]
    ]

    if not authorized and admin:
        keyboard.insert(0, [KeyboardButton(Buttons.menu.auth)])
        keyboard[0].insert(0, KeyboardButton(Buttons.menu.admin))
    else:
        if not authorized:
            keyboard[0].insert(0, KeyboardButton(Buttons.menu.auth))
        if admin:
            keyboard[0].insert(0, KeyboardButton(Buttons.menu.admin))

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def introduction_kb():
    keyboard = [
        [KeyboardButton(Buttons.menu.introduction)]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def basic_kb(buttons: list | tuple):
    return ReplyKeyboardMarkup(
        row_width=max(map(len, buttons)),
        resize_keyboard=True,
        keyboard=[*buttons] if isinstance(buttons[0], list) else [buttons]
    )


def share_phone_kb():
    keyboard = [
        [KeyboardButton(Buttons.menu.phone, request_contact=True)],
        [KeyboardButton(Buttons.menu.skip)]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)