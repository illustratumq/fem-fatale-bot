from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.database.services.enums import EventTypeEnum
from app.database.services.repos import UserRepo, ChatRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb
from app.states.states import PayoutSG


async def payout_cmd(msg: Message, user_db: UserRepo, chat_db: ChatRepo):
    chat = await chat_db.get_chat_user(msg.from_user.id)
    user = await user_db.get_user(msg.from_user.id)
    await chat.create_action_message(msg.bot, Buttons.menu.cashback)
    if not user.is_authorized:
        text = (
            '📲 Для того щоб отримати кешбек, потрібно пройти авторизацію!\n\n'
            'Бажаєш пройти авторизацію зараз? Натисни кнопку нижче'
        )
        await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.auth], [Buttons.menu.back]]))
    else:
        await user_card_cmd(msg, user_db)


async def user_card_cmd(msg: Message, user_db: UserRepo):
    user = await user_db.get_user(msg.from_user.id)
    text = (
        'Будь-ласка вкажи свою актуальну банківську карту, на яку бажаєш отримати виплату'
    )
    buttons = [[user.bankcard], [Buttons.menu.back]] if user.bankcard else [Buttons.menu.back]
    await msg.answer(text, reply_markup=basic_kb(buttons))
    await PayoutSG.Card.set()


async def save_card_cmd(msg: Message, user_db: UserRepo):
    bankcard: str = msg.text.replace(' ', '')
    user = await user_db.get_user(msg.from_user.id)
    if not bankcard.isalnum() or len(bankcard) != 16:
        await msg.answer('Упс, твоя карта введена некоректно, спробуй ще раз')
    else:
        if bankcard != user.bankcard:
            await user_db.update_user(msg.from_user.id, bankcard=bankcard)
            await msg.answer('Я зберіг твою нову карту')
        await user_comment_enter(msg)


async def user_comment_enter(msg: Message):
    await msg.answer('Напиши коментар для адміністраторів, який стосується кешбку, або пропусти цей крок',
                     reply_markup=basic_kb([[Buttons.menu.skipping], [Buttons.menu.back]]))
    await PayoutSG.Comment.set()


async def save_comment(msg: Message, state: FSMContext, chat_db: ChatRepo):
    await state.update_data(comment=msg.text)
    await save_and_send_event(msg, chat_db, state)


async def save_and_send_event(msg: Message, chat_db: ChatRepo, state: FSMContext):
    data = await state.get_data()
    description = data['comment'] if 'comment' in data.keys() else 'Користувач не залишив кометар'
    chat = await chat_db.get_chat_user(msg.from_user.id)
    await chat.create_event_message(msg.bot, EventTypeEnum.PAYOUT, description)
    await msg.answer('Твій запит надіслано! Очікуй на відповідь від адміністрації!', reply_markup=menu_kb())
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(payout_cmd, text=Buttons.menu.cashback, state='*')
    dp.register_message_handler(save_and_send_event, state=PayoutSG.Comment, text=Buttons.menu.skipping)
    dp.register_message_handler(save_card_cmd, state=PayoutSG.Card)
    dp.register_message_handler(save_comment, state=PayoutSG.Comment)
