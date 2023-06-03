import os

from aiogram import Dispatcher
from aiogram.types import Message, InputFile

from app.database.services.repos import UserRepo, MediaRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb
from app.misc.photo import make_card_photo


async def user_card_cmd(msg: Message, user_db: UserRepo):
    user = await user_db.get_user(msg.from_user.id)
    if not user.is_authorized:
        text = (
            '📲 Для того щоб користуватись карткою клієнта, потрібно пройти авторизацію!\n\n'
            'Бажаєш пройти авторизацію зараз? Натисни кнопку нижче'
        )
        await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.auth], [Buttons.menu.back]]))
    else:
        card = make_card_photo(user.my_card)
        await msg.answer_photo(InputFile(card), f'Твоя карта клієнта {user.my_card}',
                               reply_markup=basic_kb([[Buttons.menu.balance], [Buttons.menu.back]]))
        os.remove(card)


def setup(dp: Dispatcher):
    dp.register_message_handler(user_card_cmd, text=Buttons.menu.card, state='*')
