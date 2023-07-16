import os

import sqlalchemy as sa
from aiogram import Bot
from aiogram.types import InputFile, Message

from app.config import Config
from app.database.models.base import TimedBaseModel
from app.database.services.enums import EventTypeEnum
from app.misc.photo import make_event_photo


class Chat(TimedBaseModel):
    chat_id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.BIGINT, nullable=True)
    invite_link = sa.Column(sa.VARCHAR(255), nullable=False)

    async def create_event_message(self, bot: Bot, event_type: EventTypeEnum, description: str, url: bool = False,
                                   **kwargs) -> Message:
        title = {
            EventTypeEnum.AUTH: '🎉 #Новий_Клієнт',
            EventTypeEnum.HELP: '📬 #Клієнт_Задав_Питання',
            EventTypeEnum.PAYOUT: '💰 #Виплата_Кешбеку',
            EventTypeEnum.RESERV: '🛎 #Бронювання_Закладу'
        }
        text = (
            f'{title[event_type]}\n\n'
            f'<i>{description}</i>\n\n'
        )
        if url:
            config = Config.from_env()
            text += config.misc.server_host_ip + ':8000' + f'/admin/femfatale/user/{self.user_id}/change/'
        photo = make_event_photo(title[event_type][2:], description, )
        msg = await bot.send_photo(chat_id=self.chat_id, photo=InputFile(photo),
                                   caption=text, **kwargs)
        os.remove(photo)
        return msg

    async def create_action_message(self, bot: Bot, description: str):
        text = (
            f'Клієнт зайшов у розділ "{description}"'
        )
        await bot.send_message(chat_id=self.chat_id, text=text)

