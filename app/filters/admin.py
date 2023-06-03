from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message, CallbackQuery

from app.config import Config
from app.database.services.repos import ChatRepo


class IsAdminFilter(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        data: dict = ctx_data.get()
        config: Config = data['config']
        return upd.from_user.id in config.bot.admin_ids


class UserConnection(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        data = ctx_data.get()
        chat_db: ChatRepo = data['chat_db']
        if await chat_db.get_chat_user(upd.from_user.id):
            return True
        else:
            return False


class AdminConnection(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        data = ctx_data.get()
        chat_db: ChatRepo = data['chat_db']
        if await chat_db.get_chat_admin(upd.from_user.id):
            return True
        else:
            return False


class ConnectionNode(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        data = ctx_data.get()
        chat_db: ChatRepo = data['chat_db']
        if await chat_db.get_chat_admin(upd.from_user.id):
            return True
        elif await chat_db.get_chat_user(upd.from_user.id):
            return True
        else:
            return False
