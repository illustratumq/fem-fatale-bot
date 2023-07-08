from aiogram import Dispatcher

from app.handlers.admin import event, panel, database


def setup(dp: Dispatcher):
    panel.setup(dp)
    event.setup(dp)
    database.setup(dp)
