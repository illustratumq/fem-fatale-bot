import os

import sqlalchemy as sa
from aiogram import Bot
from aiogram.types import InputFile
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.markdown import hide_link
from sqlalchemy.dialects.postgresql import ENUM

from app.config import Config
from app.database.models.base import TimedBaseModel
from app.database.services.enums import EventStatusEnum, EventTypeEnum
from app.keyboards.inline.admin import event_kb
from app.misc.photo import make_event_photo


class Event(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    admin_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    message_id = sa.Column(sa.BIGINT, nullable=True)
    title = sa.Column(sa.VARCHAR(100), nullable=True)
    description = sa.Column(sa.VARCHAR(500), nullable=True)
    url = sa.Column(sa.VARCHAR(255), nullable=True)
    status = sa.Column(ENUM(EventStatusEnum), nullable=True, default=EventStatusEnum.ACTIVE)
    type = sa.Column(ENUM(EventTypeEnum), nullable=True, default=EventTypeEnum.HELP)

    async def create_event_photo(self, bot: Bot,  config: Config, event_db, user, admin=None, done=False):
        title = {
            EventTypeEnum.AUTH: 'Новий клієнт',
            EventTypeEnum.HELP: 'Клієнт задав питання',
            EventTypeEnum.PAYOUT: 'Виплата кешбеку',
            EventTypeEnum.RESERV: 'Бронювання закладу'
        }
        status = {
            EventStatusEnum.ACTIVE: 'Активний',
            EventStatusEnum.PROCESSED: f'Модерується by {admin.full_name if admin else "Невизначено"}',
            EventStatusEnum.DONE: f'Виконано by {admin.full_name if admin else "Невизнено"}'
        }
        photo = make_event_photo(title=title[self.type], description=self.description,
                                 status=status[self.status], client=user.full_name, done=done)
        msg = await bot.send_photo(config.misc.media_channel_id, InputFile(photo))
        await event_db.update_event(self.id, url=msg.url)
        os.remove(photo)

    def create_for_admin_text(self, user):
        title = {
            EventTypeEnum.AUTH: 'Новий клієнт',
            EventTypeEnum.HELP: 'Клієнт задав питання',
            EventTypeEnum.PAYOUT: 'Виплата кешбеку',
            EventTypeEnum.RESERV: 'Бронювання закладу'
        }
        text = (
            f'Подія: {title[self.type]}\n\n'
            f'Опис: {self.description}\n'
            f'Клієнт: {user.get_mentioned()}{hide_link(self.url)}'
        )
        if self.type == EventTypeEnum.PAYOUT:
            text += f'Банківська карта: {user.bankcard}'
        return text

    def create_event_text(self):
        title = {
            EventTypeEnum.AUTH: '#Новий_Клієнт',
            EventTypeEnum.HELP: '#Клієнт_Задав_Питання',
            EventTypeEnum.PAYOUT: '#Виплата_Кешбеку',
            EventTypeEnum.RESERV: '#Бронювання_Закладу'
        }
        return title[self.type] + hide_link(self.url)

    async def make_message(self, bot: Bot, config, event_db, user, admin=None, restore_keyboard: bool = False):
        await self.create_event_photo(bot, config, event_db, user, admin,
                                      done=True if self.status == EventStatusEnum.DONE else False)
        reply_markup = event_kb(await get_start_link(f'event-{self.id}'))
        if not self.message_id:
            message = await bot.send_message(config.misc.event_channel_id, self.create_event_text(),
                                             reply_markup=reply_markup)
        else:
            message = await bot.edit_message_text(
                self.create_event_text(), config.misc.event_channel_id, self.message_id,
                reply_markup=reply_markup if restore_keyboard else None)
        await event_db.update_event(self.id, message_id=message.message_id)