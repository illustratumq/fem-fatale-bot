import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, ContentTypes, ReplyKeyboardRemove

from app.config import Config
from app.database.services.enums import EventTypeEnum, EventStatusEnum, PayoutTypeEnum, UserStatusEnum
from app.database.services.repos import EventRepo, UserRepo, PayoutRepo, ChatRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb
from app.states.states import AdminEventSG

EVENT_REGEX = re.compile(r'event-(\d+)')


async def event_processing_cmd(msg: Message, user_db: UserRepo, event_db: EventRepo, deep_link: re.Match,
                               config: Config, state: FSMContext):
    event_id = int(deep_link.groups()[-1])
    event = await event_db.get_event(event_id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.PROCESSED)
    admin = await user_db.get_user(msg.from_user.id)
    user = await user_db.get_user(event.user_id)
    text = event.create_for_admin_text(user)
    await event.make_message(msg.bot, config, event_db, user, admin)
    buttons = [
        [Buttons.admin.create_message], [Buttons.admin.create_chat],
        [Buttons.admin.cancel]
    ]
    if event.type == EventTypeEnum.PAYOUT:
        buttons.insert(0, [Buttons.admin.create_payout])
    await msg.answer(text, reply_markup=basic_kb(buttons))
    await state.update_data(event_id=event_id, user_id=user.user_id)
    await AdminEventSG.Select.set()


async def event_processing_back(msg: Message, user_db: UserRepo, event_db: EventRepo,
                                config: Config, state: FSMContext):
    data = await state.get_data()
    event_id = data['event_id']
    event = await event_db.get_event(event_id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.PROCESSED)
    admin = await user_db.get_user(msg.from_user.id)
    user = await user_db.get_user(event.user_id)
    text = event.create_for_admin_text(user)
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
    await msg.answer('Дія відмінена. Ви можете повернутись до неї ще раз', reply_markup=menu_kb())
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


async def create_payout_cmd(msg: Message, state: FSMContext, user_db: UserRepo):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    text = (
        f'Створіть платіж для користувача. Це може бути поповнення або зняття балів з рахунку.\n\n'
        f'На рахунку користувача: {user.balance} балів\n\n'
        f'Оберіть відповідний тип платежу'
    )
    await msg.answer(text, reply_markup=basic_kb(
        [
            [Buttons.admin.plus], [Buttons.admin.minus],
            [Buttons.admin.back]
        ]
    ))
    await AdminEventSG.Payout.set()


async def save_payout_type(msg: Message, state: FSMContext):
    payout_type = 'minus' if msg.text == Buttons.admin.minus else 'plus'
    await state.update_data(payout_type=payout_type)
    action = {
        'minus': 'зняти з балансу',
        'plus': 'поповнити на баланс'
    }
    await msg.answer(f'Тепер оберіть скільки балів потібно {action[payout_type]}', reply_markup=basic_kb([Buttons.admin.back]))
    await AdminEventSG.Value.set()


async def save_payout_value(msg: Message, state: FSMContext, user_db: UserRepo):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    payout_value: str = msg.text
    if not payout_value.isnumeric():
        await msg.answer('Схоже це не число, відправте ще раз')
    elif data['payout_type'] == 'minus' and user.balance - int(payout_value) <= 0:
        await msg.answer(f'На балансі клієнта {user.balance} балів. '
                         f'Ви не можете зняти більше цієї суми, відправте ще раз')
    else:
        await state.update_data(payout_value=int(payout_value), payout_photo=False, payout_comment=False)
        await msg.answer('Чудово, відправте фото, яке отримає користувач, якщо це потрібно',
                         reply_markup=basic_kb([[Buttons.admin.skip], [Buttons.admin.back]]))
        await AdminEventSG.Photo.set()


async def save_payout_photo(msg: Message, state: FSMContext, user_db: UserRepo):
    await msg.answer('Фото збережено. Ви можете надіслати його повторно, щоб перезаписати')
    await state.update_data(payout_photo=msg.photo[-1].file_id)
    await confirm_payout_create(msg, state, user_db)


async def save_payout_comment(msg: Message, state: FSMContext, user_db: UserRepo):
    await msg.answer('Коментар записаний. Ви можете надіслати його повторно, щоб перезаписати')
    await state.update_data(payout_comment=msg.html_text)
    await confirm_payout_create(msg, state, user_db)


async def confirm_payout_create(msg: Message, state: FSMContext, user_db: UserRepo):
    data = await state.get_data()
    payout_type = data['payout_type']
    payout_value = data['payout_value']
    payout_photo = data['payout_photo']
    payout_comment = data['payout_comment']
    user = await user_db.get_user(data['user_id'])
    text = (
        f'Платіж для {user.get_mentioned()}\n\n'
        f'Тип платежу: {"нарахування балів" if payout_type == "plus" else "зняття балів"}\n'
        f'Кількість балів: {payout_value}\n'
    )
    if payout_comment:
        text += f'Коментар: {payout_comment}'
    if payout_photo:
        await msg.answer_photo(payout_photo, caption=text)
    else:
        await msg.answer(text)
    await msg.answer('Підтвердіть створення платежу. Ви також можете зараз додати коментар, '
                     'який побачить користувач, або не робити цього.',
                     reply_markup=basic_kb([[Buttons.admin.done_payout], [Buttons.admin.back]]))
    await AdminEventSG.ConfirmPayout.set()


async def create_payout(msg: Message, user_db: UserRepo, payout_db: PayoutRepo, state: FSMContext):
    data = await state.get_data()
    payout_type = data['payout_type']
    payout_value = data['payout_value']
    payout_photo = data['payout_photo']if data['payout_photo'] else None
    payout_comment = data['payout_comment'] if data['payout_comment'] else 'Переказв балів'
    user = await user_db.get_user(data['user_id'])
    admin = await user_db.get_user(msg.from_user.id)
    payout = await payout_db.add(
        photo_id=payout_photo, user_id=user.user_id, value=payout_value, user_answer=payout_comment,
        description=f'Переказ балів {payout_type} {payout_value} by {admin.full_name}',
        type=PayoutTypeEnum.MINUS if payout_type == 'minus' else PayoutTypeEnum.PLUS
    )
    if payout_type == 'minus':
        await user_db.update_user(user.user_id, balance=user.balance - payout_value)
    else:
        await user_db.update_user(user.user_id, balance=user.balance + payout_value)
    action = {
        'minus': 'У тебе списано',
        'plus': 'Тобі нараховано'
    }
    text = (
        f'🔔 {action[payout_type]} {payout_value} балів.'
    )
    if payout_comment:
        text += f'\n\nКоментар: {payout_comment}'
    try:
        if payout_photo:
            await msg.bot.send_photo(user.user_id, payout_photo, caption=text)
        else:
            await msg.bot.send_message(user.user_id, text)
    except:
        await user_db.update_user(user.user_id, status=UserStatusEnum.INACTIVE)
        await msg.answer('Схоже клієнт заблокував бота, і не отримає сповіщення')
    await msg.answer('Платіж створено успішно!', reply_markup=basic_kb([Buttons.admin.back]))


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
    dp.register_message_handler(event_processing_cmd, IsAdminFilter(), CommandStart(EVENT_REGEX), state='*')
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

    dp.register_message_handler(
        create_payout_cmd, IsAdminFilter(), state=AdminEventSG.Select, text=Buttons.admin.create_payout)
    dp.register_message_handler(save_payout_type, IsAdminFilter(), state=AdminEventSG.Payout)
    dp.register_message_handler(save_payout_value, IsAdminFilter(), state=AdminEventSG.Value)
    dp.register_message_handler(
        save_payout_photo, IsAdminFilter(), state=[AdminEventSG.Photo, AdminEventSG.ConfirmPayout],
        content_types=ContentTypes.PHOTO
    )
    dp.register_message_handler(
        confirm_payout_create, IsAdminFilter(), state=AdminEventSG.Photo, text=Buttons.admin.skip)
    dp.register_message_handler(
        create_payout, IsAdminFilter(), state=AdminEventSG.ConfirmPayout, text=Buttons.admin.done_payout)
    dp.register_message_handler(save_payout_comment, IsAdminFilter(), state=AdminEventSG.ConfirmPayout)