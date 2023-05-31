import logging

from aiogram import Dispatcher
from sqlalchemy.orm import sessionmaker

from app.middlewares.databse import DatabaseMiddleware
from app.middlewares.environment import EnvironmentMiddleware


log = logging.getLogger(__name__)


def setup(dp: Dispatcher, session_pool: sessionmaker, environments: dict):
    dp.setup_middleware(EnvironmentMiddleware(environments))
    dp.setup_middleware(DatabaseMiddleware(session_pool))
    log.info('Мідлварі успішно встановлені...')
