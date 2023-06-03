from app.states.base import *


class AuthSG(StatesGroup):
    Introduction = State()
    Phone = State()


class PartnerSG(StatesGroup):
    Categories = State()
    Pagination = State()


class PayoutSG(StatesGroup):
    Card = State()
    Comment = State()
    Confirm = State()
