from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.config import Config
from app.database.services.enums import EventTypeEnum
from app.database.services.repos import UserRepo, EventRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb


async def help_cmd(msg: Message, state: FSMContext):
    text = (
        'Будь-ласка напиши своє питання або проблему в одному повідомленні'
    )
    await msg.answer(text, reply_markup=basic_kb([Buttons.menu.back]))
    await state.set_state(state='help')


async def save_user_help(msg: Message, user_db: UserRepo, event_db: EventRepo, state: FSMContext,
                         config: Config):
    user = await user_db.get_user(msg.from_user.id)
    description = msg.text
    event = await event_db.add(user_id=msg.from_user.id, type=EventTypeEnum.HELP, description=description)
    await event.make_message(msg.bot, config, event_db, user)
    await msg.answer('Твій запит надіслано! Очікуй на відповідь від адміністрації!', reply_markup=menu_kb())
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(help_cmd, text=Buttons.menu.help, state='*')
    dp.register_message_handler(save_user_help, state='help')