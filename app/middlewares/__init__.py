import logging

from aiogram import Dispatcher
from sqlalchemy.orm import sessionmaker

from app.middlewares.databse import DatabaseMiddleware
from app.middlewares.environment import EnvironmentMiddleware
from app.middlewares.media import MediaMiddleware
from app.middlewares.throttling import ThrottlingMiddleware

log = logging.getLogger(__name__)


def setup(dp: Dispatcher, session_pool: sessionmaker, environments: dict):
    dp.setup_middleware(MediaMiddleware())
    dp.setup_middleware(EnvironmentMiddleware(environments))
    dp.setup_middleware(DatabaseMiddleware(session_pool))
    dp.setup_middleware(ThrottlingMiddleware())
    log.info('Мідлварі успішно встановлені...')
