from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.database.services.repos import PayoutRepo, UserRepo, MediaRepo, PartnerRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb


async def pre_paginate_payout_cmd(msg: Message, payout_db: PayoutRepo, partner_db: PartnerRepo, user_db: UserRepo,
                                  media_db: MediaRepo, state: FSMContext):
    await state.update_data(page=0)
    await paginate_payout_cmd(msg, payout_db, partner_db, user_db, media_db, state)


async def paginate_payout_cmd(msg: Message, payout_db: PayoutRepo, partner_db: PartnerRepo, user_db: UserRepo,
                              media_db: MediaRepo, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    user = await user_db.get_user(msg.from_user.id)

    payouts = await payout_db.get_payout_user(msg.from_user.id)
    if not payouts:
        await msg.answer('Твоя історія балансу поки що ненаповнена')
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
        f'🧾 Номер [{payouts.index(payout) + 1}/{len(payouts)}]\n\n'
        f'{await payout.construct_payout_text(partner_db)}'
    )

    await state.update_data(page=page)
    await state.set_state(state='pag_payout')

    reply_markup = basic_kb(
        [
            [Buttons.history.prev, Buttons.history.next],
            [Buttons.back.card]
        ]
    )

    if payout.media_id:
        media = await media_db.get_media(payout.media_id)
        if media.is_media_group():
            await msg.answer_media_group(media.get_media_group(text))
        else:
            await msg.answer_photo(media.files[0], caption=text)
        await msg.answer('Переглянте наступний платіж, або поверніться назад', reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)


def setup(dp: Dispatcher):
    dp.register_message_handler(pre_paginate_payout_cmd, text=Buttons.menu.history, state='*')
    dp.register_message_handler(paginate_payout_cmd, state='pag_payout')