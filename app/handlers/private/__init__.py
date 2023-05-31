from aiogram import Dispatcher

from app.handlers.private import start


def setup(dp: Dispatcher):
    start.setup(dp)
