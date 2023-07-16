from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.database.services.enums import EventTypeEnum
from app.database.services.repos import UserRepo, ChatRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb


async def help_cmd(msg: Message, state: FSMContext):
    text = (
        'Будь-ласка напиши своє питання або проблему'
    )
    await msg.answer(text, reply_markup=basic_kb([Buttons.menu.back]))
    await state.set_state(state='help')


async def save_user_help(msg: Message, state: FSMContext,
                         chat_db: ChatRepo):
    description = msg.text
    chat = await chat_db.get_chat_user(msg.from_user.id)
    await chat.create_event_message(msg.bot, EventTypeEnum.HELP, description)
    await msg.answer('Твій запит надіслано! Очікуй на відповідь від адміністрації!', reply_markup=menu_kb())
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(help_cmd, text=Buttons.menu.help, state='*')
    dp.register_message_handler(save_user_help, state='help')