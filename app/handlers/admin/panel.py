from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.database.services.repos import UserRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb


async def admin_panel_cmd(msg: Message, state: FSMContext):
    reply_markup = basic_kb([
        [Buttons.admin.database, Buttons.admin.search],
        [Buttons.back.menu]
    ])
    await msg.answer('Ви перейшли в адмін панель', reply_markup=reply_markup)
    await state.finish()


async def search_user_cmd(msg: Message, state: FSMContext):
    await msg.answer('Напишіть номер карти, телефону або ім\'я клієнта', reply_markup=basic_kb([Buttons.admin.to_admin]))
    await state.set_state(state='search')


async def check_input_data(msg: Message, user_db: UserRepo, state: FSMContext):
    search_funcs = [
        user_db.get_user_card,
        user_db.get_user_name
    ]
    if len(msg.text) >= 9:
        search_funcs.insert(0, user_db.get_user_phone)
    for search_func in search_funcs:
        user = await search_func(msg.text)
        if user:
            await msg.answer(user.user_info_text(), reply_markup=basic_kb([
                [Buttons.admin.create_payout_panel],
                [Buttons.admin.create_chat_panel],
                [Buttons.admin.to_admin]
            ]))
            await state.update_data(user_id=user.user_id)
            await state.set_state(state='select_action')


def setup(dp: Dispatcher):
    dp.register_message_handler(
        admin_panel_cmd, IsAdminFilter(), text=(Buttons.menu.admin, Buttons.admin.to_admin), state='*')
    dp.register_message_handler(search_user_cmd, IsAdminFilter(), text=Buttons.admin.search, state='*')
    dp.register_message_handler(check_input_data, IsAdminFilter(), state='search')
