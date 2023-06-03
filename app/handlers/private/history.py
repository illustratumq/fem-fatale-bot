from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.database.services.repos import PayoutRepo, UserRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb


async def pre_paginate_payout_cmd(msg: Message, payout_db: PayoutRepo, user_db: UserRepo, state: FSMContext):
    await state.update_data(page=0)
    await paginate_payout_cmd(msg, payout_db, user_db, state)


async def paginate_payout_cmd(msg: Message, payout_db: PayoutRepo, user_db: UserRepo, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    user = await user_db.get_user(msg.from_user.id)

    payouts = await payout_db.get_all()
    if not payouts:
        await msg.answer('Твоя історія балансу поки що нехаповнена')
        return

    if msg.text == Buttons.history.next:
        if len(payouts) > 1:
            page = (page + 1) % len(payouts)
        else:
            await msg.answer('У тебе тільки один платіж')
            return
    elif msg.text == Buttons.history.prev:
        if len(payouts) > 1:
            page = (page - 1) % len(payouts)
        else:
            await msg.answer('У тебе тільки один платіж')
            return

    payout: PayoutRepo.model = payouts[page]
    text = (
        f'Номер {payouts.index(payout) + 1}/{len(payouts)}\n\n'
        f'{payout.construct_payout_text()}'
    )

    await state.update_data(page=page)
    await state.set_state(state='pag_payout')

    reply_markup = basic_kb(
        [
            [Buttons.history.prev, Buttons.history.next],
            [Buttons.menu.back]
        ]
    )

    if payout.photo_id:
        await msg.answer_photo(payout.photo_id, caption=text, reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)


def setup(dp: Dispatcher):
    dp.register_message_handler(pre_paginate_payout_cmd, text=Buttons.menu.balance, state='*')
    dp.register_message_handler(paginate_payout_cmd, state='pag_payout')