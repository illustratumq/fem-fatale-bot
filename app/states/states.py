from app.states.base import *


class AuthSG(StatesGroup):
    Introduction = State()
    Phone = State()


class PartnerSG(StatesGroup):
    Categories = State()
    City = State()
    Pagination = State()


class PayoutSG(StatesGroup):
    Card = State()
    Comment = State()
    Confirm = State()


class AdminEventSG(StatesGroup):
    Select = State()
    OneTimeMessage = State()
    Payout = State()
    Confirm = State()


class AdminPanelSG(StatesGroup):
    OneTimeMessage = State()
    Confirm = State()
