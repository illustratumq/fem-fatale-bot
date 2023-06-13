from aiogram import Dispatcher

from app.handlers.private import start, card, partners, media, news, payout, reserv, help, history, info


def setup(dp: Dispatcher):
    start.setup(dp)
    card.setup(dp)
    reserv.setup(dp)
    partners.setup(dp)
    news.setup(dp)
    media.setup(dp)
    payout.setup(dp)
    help.setup(dp)
    history.setup(dp)
    info.setup(dp)
