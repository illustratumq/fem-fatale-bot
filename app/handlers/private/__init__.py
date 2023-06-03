from aiogram import Dispatcher

from app.handlers.private import start, card, partners, media, news


def setup(dp: Dispatcher):
    start.setup(dp)
    card.setup(dp)
    partners.setup(dp)
    news.setup(dp)
    media.setup(dp)
