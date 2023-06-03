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


class AdminEventSG(StatesGroup):
    Select = State()
    OneTimeMessage = State()
    Payout = State()
    Value = State()
    Photo = State()
    Confirm = State()
    ConfirmPayout = State()


class AdminPayoutSG(StatesGroup):
    Payout = State()
    Value = State()
    Photo = State()
    Confirm = State()