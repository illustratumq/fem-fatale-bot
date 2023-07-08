from typing import Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.services.repos import *


class DatabaseMiddleware(LifetimeControllerMiddleware):

    def __init__(self, session_pool: sessionmaker):
        self.session_pool = session_pool
        super().__init__()

    async def pre_process(self, obj: TelegramObject, data: dict, *args: Any):
        session: AsyncSession = self.session_pool()
        data['session'] = session
        data['user_db'] = UserRepo(session)
        data['partner_db'] = PartnerRepo(session)
        data['article_db'] = ArticleRepo(session)
        data['event_db'] = EventRepo(session)
        data['media_db'] = MediaRepo(session)
        data['payout_db'] = PayoutRepo(session)

    async def post_process(self, obj: TelegramObject, data: dict, *args: Any):
        if session := data.get('session', None):
            session: AsyncSession
            await session.close()
