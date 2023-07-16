from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message, CallbackQuery, ContentTypes, ContentType

from app.config import Config


class IsAdminFilter(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        data: dict = ctx_data.get()
        config: Config = data['config']
        return upd.from_user.id in config.bot.admin_ids


class IsDialogMessage(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        return upd.content_type in (
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.VOICE,
            ContentType.AUDIO,
            ContentType.CONTACT,
            ContentType.DOCUMENT,
            ContentType.ANIMATION,
            ContentType.VIDEO_NOTE,
            ContentType.LOCATION,
            ContentType.STICKER,
        )
