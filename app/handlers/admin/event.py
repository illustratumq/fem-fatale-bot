from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.config import Config
from app.database.services.enums import EventTypeEnum, EventStatusEnum
from app.database.services.repos import EventRepo, UserRepo, ChatRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb
from app.states.states import AdminEventSG


async def event_processing_back(msg: Message, user_db: UserRepo, event_db: EventRepo,
                                config: Config, state: FSMContext):
    data = await state.get_data()
    event_id = data['event_id']
    event = await event_db.get_event(event_id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.PROCESSED)
    admin = await user_db.get_user(msg.from_user.id)
    user = await user_db.get_user(event.user_id)
    url = config.misc.server_host_ip + ':8000' + f'/admin/femfatale/user/{user.user_id}/change/'
    text = event.create_for_admin_text(user) + f'\n\n🌍 <a href="{url}">Перейти в адмін панель</a>'
    await event.make_message(msg.bot, config, event_db, user, admin)
    buttons = [
        [Buttons.admin.make_done],
        [Buttons.admin.create_message], [Buttons.admin.create_chat],
        [Buttons.admin.cancel]
    ]
    if event.type == EventTypeEnum.PAYOUT:
        buttons.insert(1, [Buttons.admin.create_payout])
    await msg.answer(text, reply_markup=basic_kb(buttons))
    await state.update_data(event_id=event_id, user_id=user.user_id)
    await AdminEventSG.Select.set()


async def cancel_processing(msg: Message, user_db: UserRepo, event_db: EventRepo, config: Config, state: FSMContext):
    data = await state.get_data()
    event_id = data['event_id']
    event = await event_db.get_event(event_id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.ACTIVE)
    user = await user_db.get_user(event.user_id)
    await event.make_message(msg.bot, config, event_db, user, restore_keyboard=True)
    await msg.answer('Дія відмінена. Ви можете повернутись до неї ще раз', reply_markup=menu_kb(admin=True))
    await state.finish()


async def done_processing_confirm(msg: Message):
    await msg.answer('Підтвердіть, що дійсно хочете завершити це звернення від клієнта. Після завершення, '
                     'ви вже не зможете відповісти клієнту на це питання.',
                     reply_markup=basic_kb([[Buttons.admin.make_done], [Buttons.admin.back]]))
    await AdminEventSG.Confirm.set()


async def done_processing(msg: Message, user_db: UserRepo, event_db: EventRepo, config: Config, state: FSMContext):
    data = await state.get_data()
    event_id = data['event_id']
    event = await event_db.get_event(event_id)
    admin = await user_db.get_user(msg.from_user.id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.DONE)
    user = await user_db.get_user(event.user_id)
    await event.make_message(msg.bot, config, event_db, user, admin)
    await msg.answer('Дія завершена 👌', reply_markup=menu_kb())
    await state.finish()


async def one_time_message_cmd(msg: Message, user_db: UserRepo, state: FSMContext):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    text = (
        'Разове повідомлення довзоляє користувачу отримати необхідну інформацію одним повідомленням, '
        'а Адміністратору - відповісти клієнту без створення чату!\n\n'
        f'Будь-ласка напишіть свою відповідь для {user.get_mentioned()}'
    )
    await msg.answer(text, reply_markup=basic_kb([Buttons.admin.back]))
    await AdminEventSG.OneTimeMessage.set()


async def save_one_time_message(msg: Message, state: FSMContext):
    await state.update_data(admin_answer=msg.html_text)
    text = (
        'Повідомлення успішно записано, якщо бажаєте змінити його вміст, '
        'відправт відредагований текст просто зараз.\n\n'
        'Якщо все вірно - підтвердіть відправку повідомлення'
    )
    await msg.reply(text, reply_markup=basic_kb([[Buttons.admin.create_message], [Buttons.admin.back]]))
    await AdminEventSG.Confirm.set()


async def send_one_time_message(msg: Message, user_db: UserRepo, event_db: EventRepo,
                                config: Config, state: FSMContext):
    data = await state.get_data()
    event = await event_db.get_event(data['event_id'])
    action = {
        EventTypeEnum.PAYOUT: 'на твій запит про виплату кешбеку',
        EventTypeEnum.HELP: f'на твоє питання "{event.description[:15]}..."',
        EventTypeEnum.RESERV: f'на твій запит на бронювання закладу\n\n{event.description}',
        EventTypeEnum.AUTH: f'на твою реєстрацію у нашому сервісі'
    }
    text = (
        f'Адміністратор ФемФаталь відповів {action[event.type]}:\n\n'
        f'Відповідь: <i>{data["admin_answer"]}</i>'
    )
    await msg.bot.send_message(data['user_id'], text=text)
    await msg.answer('Повідомлення успішно відправлено')
    await event_processing_back(msg, user_db, event_db, config, state)


async def create_chat(msg: Message, user_db: UserRepo, chat_db: ChatRepo, event_db: EventRepo, state: FSMContext):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    event = await event_db.get_event(data['event_id'])
    chat = await chat_db.add(user_id=data['user_id'], admin_id=msg.from_user.id, event_id=data['event_id'])
    await state.update_data(chat_id=chat.chat_id)
    action = {
        EventTypeEnum.AUTH: 'на ваш запиш щодо реєстрації',
        EventTypeEnum.HELP: 'на ваше питання',
        EventTypeEnum.PAYOUT: 'на ваш запит по виплаті кешбеку',
        EventTypeEnum.RESERV: 'на ваш запит по бронюванню закладу'
    }
    to_admin_text = (
        '💬 Ви знаходитесь в режимі спілкування, всі ваші повідомлення будуть транслюватись ботом користувачу.\n\n'
        'Для того, щоб завершити спілкування, будь ласка використовуйте кнопки нижче.\n\n'
        f'#Чат_номер_{chat.chat_id}.'
    )
    to_user_text = (
        f'💬 Вітаю {user.first_name}, {action[event.type]} відповість менеджер ФемФаталь\n\n'
        f'Якщо ви бажаєте завершити діалог, будь ласка скористайтеся кнопкою нижче'
    )
    await msg.answer(to_admin_text, reply_markup=basic_kb([Buttons.admin.cancel_chat]))
    await msg.bot.send_message(user.user_id, to_user_text, reply_markup=ReplyKeyboardRemove())


def setup(dp: Dispatcher):
    dp.register_message_handler(
        cancel_processing, IsAdminFilter(), text=Buttons.admin.cancel, state=AdminEventSG.Select)
    dp.register_message_handler(
        create_chat, IsAdminFilter(), text=Buttons.admin.create_chat, state=AdminEventSG.Select)
    dp.register_message_handler(
        one_time_message_cmd, IsAdminFilter(), text=Buttons.admin.create_message, state=AdminEventSG.Select)
    dp.register_message_handler(save_one_time_message, IsAdminFilter(), state=AdminEventSG.OneTimeMessage)
    dp.register_message_handler(event_processing_back, IsAdminFilter(), text=Buttons.admin.back, state='*')
    dp.register_message_handler(
        send_one_time_message, IsAdminFilter(), text=Buttons.admin.create_message, state=AdminEventSG.Confirm)
    dp.register_message_handler(
        done_processing_confirm, IsAdminFilter(), state=AdminEventSG.Select, text=Buttons.admin.make_done)
    dp.register_message_handler(
        done_processing, IsAdminFilter(), state=AdminEventSG.Confirm, text=Buttons.admin.make_done)
