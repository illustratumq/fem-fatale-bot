import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, ContentTypes

from app.config import Config
from app.database.services.enums import UserStatusEnum, EventTypeEnum, UserRoleEnum, EventStatusEnum
from app.database.services.repos import UserRepo, EventRepo, PayoutRepo
from app.filters import IsAdminFilter
from app.keyboards.reply.menu import menu_kb, introduction_kb, share_phone_kb, Buttons, basic_kb
from app.states.states import AuthSG, AdminEventSG

EVENT_REGEX = re.compile(r'event-(\d+)')


async def start_cmd(msg: Message, user_db: UserRepo, state: FSMContext):
    user = await user_db.get_user(msg.from_user.id)
    if user is None:
        await introduction_cmd(msg)
    else:
        if user.status == UserStatusEnum.INACTIVE:
            await user_db.update_user(user.user_id, status=UserStatusEnum.ACTIVE)
        admin = user.role == UserRoleEnum.ADMIN
        await msg.answer(f'Ви перейшли в Гловне меню 👋', reply_markup=menu_kb(user.is_authorized, admin))
        await state.finish()


async def introduction_cmd(msg: Message):
    text = (
        f'Привіт, {msg.from_user.first_name} 👋\n\n'
        f'Ми дуже раді бачити тебе в нашому боті! Наша мета зробити спілкування '
        f'з тобою простішим та доступнішим!🔝\n\n'
        '<b>Тут ти завжди зможеш:</b>\n\n'
        '• Мати при собі номер своєї карти та бачити історію свого балансу\n'
        '• Подивитись список партнерів з актуальною інформацією\n'
        '• Замовити бронювання у закладах наших партнерів або виплату кешбеку\n'
        '•  Отримувати повідомленя про круті акціїї та новини\n\n'
        '<b>Для того щоб користуватись ботом використовуй кнопки, які завжи будуть зниу екрану 👇</b>'
    )
    await msg.answer(text, reply_markup=introduction_kb())
    await AuthSG.Introduction.set()


async def authorization_cmd(msg: Message):
    text = (
        '📲 Поділись своїм номером телефону, щоб ми змогли впізнати тебе! Натисни на кнопку нижче!\n\n'
        'Ти також можеш пропустити цей крок, і зробити це пізніше.'
    )
    await msg.answer(text, reply_markup=share_phone_kb())
    await AuthSG.Phone.set()


async def skip_authorization_cmd(msg: Message, user_db: UserRepo, event_db: EventRepo, config: Config,
                                 state: FSMContext):
    user = await user_db.get_user(msg.from_user.id)
    data = await state.get_data()
    phone = data['phone'] if 'phone' in data.keys() else None
    if not user or all([user, phone]):
        role = UserRoleEnum.ADMIN if msg.from_user.id in config.bot.admin_ids else UserRoleEnum.USER
        user = await user_db.add(user_id=msg.from_user.id, full_name=msg.from_user.full_name,
                                 phone=phone, info='Новий клієнт. Карта видана автоматично',
                                 role=role)
        text = (
            f'<b>Здається, Ти наш новий клієнт! 🎉</b>\n\n'
            f'Або раніше використовувала(-вав) інший номер телефону при реєстрації '
            f'в мобільному додатку Femme Fatale.\n\n'
        )
        if phone:
            await user_db.generate_user_card(msg.from_user.id)
            await user_db.update_user(msg.from_user.id, status=UserStatusEnum.ACTIVE)
            user = await user_db.get_user(msg.from_user.id)
            text += f'Ми автоматично видали тобі карту клієнта {user.card}'
        else:
            event = await event_db.add(
                user_id=msg.from_user.id, description='Користувач не авторизувався. Необхідно видати карту клієнта',
                type=EventTypeEnum.AUTH
            )
            await event.make_message(msg.bot, config, event_db, user)
        await msg.answer(text, reply_markup=menu_kb())
        await state.finish()
    else:
        await start_cmd(msg, user_db, state)


async def search_user_cmd(msg: Message, user_db: UserRepo, payout_db: PayoutRepo, state: FSMContext,
                          event_db: EventRepo, config: Config):
    phone = msg.contact.phone_number.replace('+', '').replace(' ', '')
    user_by_phone = await user_db.get_user_phone(phone)
    if not user_by_phone:
        await state.update_data(phone=phone)
        await skip_authorization_cmd(msg, user_db, event_db, config, state)
    else:
        role = UserRoleEnum.ADMIN if msg.from_user.id in config.bot.admin_ids else UserRoleEnum.USER

        await msg.answer(f'Ура, ми змогли розпізнати тебе, {user_by_phone.first_name.capitalize()}! 🎉')
        payout = await payout_db.get_user_default(user_id=user_by_phone.user_id)
        #  Шукаємо користувача по цьому юзер айді, я якщо він є видаляємо його

        user_by_id = await user_db.get_user(msg.from_user.id)
        if user_by_id:
            await user_db.delete_user(user_by_id.user_id)

        #  Дані користувача, знайденого за номером телефону оновлюємо новим адйі та статусом
        new_user_data = user_by_phone.as_dict()
        new_user_data.update(
            user_id=msg.from_user.id, status=UserStatusEnum.ACTIVE, role=role
        )
        await user_db.add(**new_user_data)
        await payout_db.update_payout(payout.id, user_id=msg.from_user.id)

        #  Видаляємо дані юзера знайденого за номером телефону
        await user_db.delete_user(user_by_phone.user_id)
        await start_cmd(msg, user_db, state)
        await state.finish()


async def event_processing_cmd(msg: Message, user_db: UserRepo, event_db: EventRepo, deep_link: re.Match,
                               config: Config, state: FSMContext):
    event_id = int(deep_link.groups()[-1])
    event = await event_db.get_event(event_id)
    await event_db.update_event(event_id, admin_id=msg.from_user.id, status=EventStatusEnum.PROCESSED)
    admin = await user_db.get_user(msg.from_user.id)
    user = await user_db.get_user(event.user_id)
    url = config.misc.server_host_ip + ':8000' + f'/admin/femfatale/user/{user.user_id}/change/'
    text = event.create_for_admin_text(user) + f'\n\n🌍 <a href="{url}">Перейти в адмін панель</a>'
    await event.make_message(msg.bot, config, event_db, user, admin)
    buttons = [
        [Buttons.admin.create_message], [Buttons.admin.create_chat],
        [Buttons.admin.make_done],
        [Buttons.admin.cancel]
    ]
    if event.type == EventTypeEnum.PAYOUT:
        buttons.insert(0, [Buttons.admin.create_payout])
    await msg.answer(text, reply_markup=basic_kb(buttons))
    await state.update_data(event_id=event_id, user_id=user.user_id)
    await AdminEventSG.Select.set()


def setup(dp: Dispatcher):
    dp.register_message_handler(event_processing_cmd, IsAdminFilter(), CommandStart(EVENT_REGEX), state='*')
    dp.register_message_handler(start_cmd, CommandStart(), state='*')
    dp.register_message_handler(start_cmd, text=(Buttons.menu.back, Buttons.back.menu), state='*')
    dp.register_message_handler(authorization_cmd, text=Buttons.menu.auth)
    dp.register_message_handler(authorization_cmd, state=AuthSG.Introduction, text=Buttons.menu.introduction)
    dp.register_message_handler(search_user_cmd, state=AuthSG.Phone, content_types=ContentTypes.CONTACT)
    dp.register_message_handler(skip_authorization_cmd, state=AuthSG.Phone, text=Buttons.menu.skip)