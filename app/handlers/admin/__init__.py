from aiogram import Dispatcher

from app.handlers.admin import event, panel, payout, database, chat


def setup(dp: Dispatcher):
    chat.setup(dp)
    panel.setup(dp)
    event.setup(dp)
    payout.setup(dp)
    database.setup(dp)