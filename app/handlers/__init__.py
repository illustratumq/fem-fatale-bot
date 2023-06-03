from aiogram import Dispatcher

from app.handlers import private, admin
from app.handlers.private import start


def setup(dp: Dispatcher):
    admin.setup(dp)
    private.setup(dp)
