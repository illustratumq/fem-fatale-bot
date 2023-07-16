from aiogram import Dispatcher

from app.handlers.admin import panel, database


def setup(dp: Dispatcher):
    panel.setup(dp)
    database.setup(dp)
