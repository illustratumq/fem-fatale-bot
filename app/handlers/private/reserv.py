from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.config import Config
from app.database.services.enums import EventTypeEnum
from app.database.services.repos import UserRepo, EventRepo, PartnerRepo
from app.keyboards.reply.menu import basic_kb, Buttons, menu_kb


async def reserv_cmd(msg: Message, user_db: UserRepo, partner_db: PartnerRepo, state: FSMContext):
    user = await user_db.get_user(msg.from_user.id)
    if not user.is_authorized:
        text = (
            '📲 Для того щоб отримати кешбек, потрібно пройти авторизацію!\n\n'
            'Бажаєш пройти авторизацію зараз? Натисни кнопку нижче'
        )
        await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.auth], [Buttons.menu.back]]))
    else:
        text = (
            'Для того щоб забронювати заклад, будь-ласка обов\'язково вкажи:\n'
            '- Назву закладу\n'
        )
        data = await state.get_data()
        if 'partner_id' in data.keys():
            partner = await partner_db.get_partner(data['partner_id'])
            text = (
                f'Для того щоб забронювати заклад {partner.name}, будь-ласка обов\'язково вкажи:\n'
            )
        text += (
            '- Дату та час\n'
            '- Кількість гостей\n'
            '- Ім\'я на яке буде бронюватись заклад\n\n'
            'На додаток, ти також можеш написати будь-який коментар.'
        )
        await msg.answer(text, reply_markup=basic_kb([Buttons.menu.back]))
        await state.set_state(state='reserv')


async def save_user_comment(msg: Message, user_db: UserRepo, event_db: EventRepo, state: FSMContext,
                            config: Config, partner_db: PartnerRepo):
    data = await state.get_data()
    description = msg.text
    if 'partner_id' in data.keys():
        partner = await partner_db.get_partner(data['partner_id'])
        description = f'Заклад {partner.name}. {description}'
    user = await user_db.get_user(msg.from_user.id)
    event = await event_db.add(user_id=msg.from_user.id, type=EventTypeEnum.RESERV, description=description)
    await event.make_message(msg.bot, config, event_db, user)
    await msg.answer('Твій запит надіслано! Очікуй на відповідь від адміністрації!', reply_markup=menu_kb())
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(reserv_cmd, text=Buttons.menu.reserv, state='*')
    dp.register_message_handler(save_user_comment, state='reserv')