from aiogram import Dispatcher

from app.handlers import private


def setup(dp: Dispatcher):
    private.setup(dp)
