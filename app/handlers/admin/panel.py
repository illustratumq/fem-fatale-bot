from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.config import Config
from app.database.services.repos import UserRepo, MediaRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb
from app.states.states import AdminPanelSG


async def admin_panel_cmd(msg: Message, state: FSMContext, config: Config):
    reply_markup = basic_kb([
        [Buttons.admin.database, Buttons.admin.search],
        [Buttons.admin.media],
        [Buttons.back.menu]
    ])
    text = (
        'Ви перейшли в адмін панель\n\n'
        '/add - Додати нову медіа групу\n\n'
        f'Перейти на сайт: {"http://" + config.misc.server_host_ip + ":8000/admin"}'
    )
    await msg.answer(text, reply_markup=reply_markup)
    await state.finish()


async def admin_media_cmd(msg: Message, media_db: MediaRepo, state: FSMContext):
    medias = await media_db.get_all()
    buttons = []
    for media in medias[:5]:
        buttons.append([media.name])
    buttons.append([Buttons.admin.to_admin])
    await msg.answer('Оберіть медіа зі списку, або введість номер медіа групи вручну',
                     reply_markup=basic_kb(buttons))
    await state.set_state(state='select_media')


async def admin_media_viewer(msg: Message, media_db: MediaRepo, state: FSMContext):
    key: str = msg.text
    if key.isalnum():
        media = await media_db.get_media(int(key))
    else:
        media = await media_db.get_media_name(key)
    if not media:
        await msg.answer('Не знайшов таку медіа групу, спробуйте ще раз')
        return
    reply_markup = basic_kb([
        [Buttons.admin.to_admin],
        [Buttons.back.media]
    ])
    if media.is_media_group():
        await msg.answer('Обрана медіа група', reply_markup=reply_markup)
        await msg.answer_media_group(media.get_media_group(media.name))
    else:
        await msg.answer_photo(media.files[0], media.name, reply_markup=reply_markup)
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
                [Buttons.admin.create_message],
                [Buttons.admin.create_chat],
                [Buttons.admin.to_admin]
            ]))
            await state.update_data(user_id=user.user_id)
            await state.set_state(state='select_action')


async def one_time_message_panel_cmd(msg: Message, user_db: UserRepo, state: FSMContext):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    text = (
        'Разове повідомлення довзоляє користувачу отримати необхідну інформацію одним повідомленням, '
        'а Адміністратору - відповісти клієнту без створення чату!\n\n'
        f'Будь-ласка напишіть свою відповідь для {user.get_mentioned()}'
    )
    await msg.answer(text, reply_markup=basic_kb([Buttons.admin.back]))
    await AdminPanelSG.OneTimeMessage.set()


async def save_one_time_message(msg: Message, state: FSMContext):
    await state.update_data(admin_answer=msg.html_text)
    text = (
        'Повідомлення успішно записано, якщо бажаєте змінити його вміст, '
        'відправт відредагований текст просто зараз.\n\n'
        'Якщо все вірно - підтвердіть відправку повідомлення'
    )
    await msg.reply(text, reply_markup=basic_kb([[Buttons.admin.create_message], [Buttons.admin.back]]))
    await AdminPanelSG.Confirm.set()


async def send_one_time_message(msg: Message, user_db: UserRepo, state: FSMContext):
    data = await state.get_data()
    text = (
        f'Адміністратор ФемФаталь написав повідомлення:\n\n'
        f'<i>{data["admin_answer"]}</i>'
    )
    user = await user_db.get_user(data['user_id'])
    await msg.bot.send_message(data['user_id'], text=text)
    await msg.answer('Повідомлення успішно відправлено')
    await msg.answer(user.user_info_text(), reply_markup=basic_kb([
        [Buttons.admin.create_message],
        [Buttons.admin.create_chat],
        [Buttons.admin.to_admin]
    ]))
    await state.update_data(user_id=user.user_id)
    await state.set_state(state='select_action')


def setup(dp: Dispatcher):
    dp.register_message_handler(
        admin_panel_cmd, IsAdminFilter(), text=(Buttons.menu.admin, Buttons.admin.to_admin), state='*')
    dp.register_message_handler(
        admin_media_cmd, IsAdminFilter(), text=(Buttons.admin.media, Buttons.back.media), state='*')
    dp.register_message_handler(admin_media_viewer, IsAdminFilter(), state='select_media')
    dp.register_message_handler(search_user_cmd, IsAdminFilter(), text=Buttons.admin.search, state='*')
    dp.register_message_handler(check_input_data, IsAdminFilter(), state='search')
    dp.register_message_handler(one_time_message_panel_cmd, IsAdminFilter(), text=Buttons.admin.create_message,
                                state='select_action')
    dp.register_message_handler(save_one_time_message, IsAdminFilter(), state=AdminPanelSG.OneTimeMessage)
    dp.register_message_handler(send_one_time_message, IsAdminFilter(), state=AdminPanelSG.Confirm,
                                text=Buttons.admin.create_message)