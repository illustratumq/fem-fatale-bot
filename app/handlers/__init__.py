from aiogram import Dispatcher

from app.handlers import private, admin
from app.handlers.private import start
from app.handlers import dialog


def setup(dp: Dispatcher):
    private.setup(dp)
    admin.setup(dp)
    dialog.setup(dp)
