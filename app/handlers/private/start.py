from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message

from app.database.services.repos import DatabaseRepo


async def start_cmd(msg: Message, db: DatabaseRepo):
    user = await db.user_db.get_user(msg.from_user.id)
    await msg.answer(f'Мої вітаннячка, #{user}')


def setup(dp: Dispatcher):
    dp.register_message_handler(start_cmd, CommandStart(), state='*')
