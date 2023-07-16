import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, ContentTypes

from app.config import Config
from app.database.services.enums import UserStatusEnum, EventTypeEnum, UserRoleEnum
from app.database.services.repos import UserRepo, PayoutRepo, ChatRepo
from app.keyboards.reply.menu import menu_kb, introduction_kb, share_phone_kb, Buttons
from app.misc.userbot import UserbotController
from app.states.states import AuthSG

EVENT_REGEX = re.compile(r'event-(\d+)')


async def start_cmd(msg: Message, user_db: UserRepo, chat_db: ChatRepo, userbot: UserbotController,
                    state: FSMContext, config: Config):
    user = await user_db.get_user(msg.from_user.id)
    if user is None:
        await introduction_cmd(msg, chat_db, userbot, config)
    elif msg.text == Buttons.menu.dialog:
        await msg.answer('Для того щоб зв\'язатись або відповісти нам, просто відправ повідомлення в цей чат.',
                         reply_markup=menu_kb(user.is_authorized))
        await state.finish()
    else:
        if user.status == UserStatusEnum.INACTIVE:
            await user_db.update_user(user.user_id, status=UserStatusEnum.ACTIVE)
        admin = user.role == UserRoleEnum.ADMIN
        await msg.answer(f'Ви перейшли в Гловне меню 👋', reply_markup=menu_kb(user.is_authorized, admin))
        await state.finish()


async def introduction_cmd(msg: Message, chat_db: ChatRepo, userbot: UserbotController, config: Config):
    text = (
        f'Привіт, {msg.from_user.first_name} 👋\n\n'
        f'Ми дуже раді бачити тебе в нашому боті! Наша мета зробити спілкування '
        f'з тобою простішим та доступнішим!🔝\n\n'
        '<b>Тут ти завжди зможеш:</b>\n\n'
        '• Мати при собі номер своєї карти та бачити історію свого балансу\n'
        '• Подивитись список партнерів з актуальною інформацією\n'
        '• Замовити бронювання у закладах наших партнерів або виплату кешбеку\n'
        '•  Отримувати повідомленя про круті акціїї та новини\n\n'
        '<b>Для того щоб користуватись меню ботом використовуй кнопки, які завжи будуть знизу екрану, як ця 👇</b>'
    )
    await msg.answer(text, reply_markup=introduction_kb())
    await AuthSG.Introduction.set()
    if msg.from_user.id not in config.bot.admin_ids:
        await create_user_dialog(msg, chat_db, userbot)


async def help_guide_cmd(msg: Message):
    text = (
        'Для того щоб зв\'ятись з нами, просто напиши повідмолення в цей чат, '
        'після чого, адміністратор відповість тобі через бота.'
    )
    await msg.answer(text, reply_markup=introduction_kb(version_two=True))
    await AuthSG.HelpGuide.set()


async def authorization_cmd(msg: Message):
    text = (
        '📲 Поділись своїм номером телефону, щоб ми змогли впізнати тебе! Натисни на кнопку нижче!\n\n'
        'Ти також можеш пропустити цей крок, і зробити це пізніше.'
    )
    await msg.answer(text, reply_markup=share_phone_kb())
    await AuthSG.Phone.set()


async def skip_authorization_cmd(msg: Message, user_db: UserRepo, config: Config,
                                 userbot: UserbotController, state: FSMContext, chat_db: ChatRepo):
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
        chat = await chat_db.get_chat_user(msg.from_user.id)
        if phone:
            await user_db.generate_user_card(msg.from_user.id)
            await user_db.update_user(msg.from_user.id, status=UserStatusEnum.ACTIVE)
            user = await user_db.get_user(msg.from_user.id)
            text += f'Ми автоматично видали тобі карту клієнта {user.card}'
            description = (
                f'Новий клієнт {msg.from_user.full_name} зареєструвався в боті! Карта клієнта видана' 
                f'автоматично: {user.my_card}'
            )
        else:
            description = (
                f'Новий клієнт {msg.from_user.full_name} зареєструвався в боті! Карта кілєнта НЕ видана.'
            )
        if chat:
            message = await chat.create_event_message(msg.bot, EventTypeEnum.AUTH, description=description, url=True)
            await msg.bot.pin_chat_message(chat_id=chat.chat_id, message_id=message.message_id)
        await msg.answer(text, reply_markup=menu_kb())
        await state.finish()
    else:
        await start_cmd(msg, user_db, chat_db, userbot, state, config)


async def search_user_cmd(msg: Message, user_db: UserRepo, payout_db: PayoutRepo, state: FSMContext,
                          config: Config, chat_db: ChatRepo, userbot: UserbotController):
    phone = msg.contact.phone_number.replace('+', '').replace(' ', '')
    user_by_phone = await user_db.get_user_phone(phone)
    if not user_by_phone:
        await state.update_data(phone=phone)
        await skip_authorization_cmd(msg, user_db, config, userbot, state, chat_db)
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
        new_user = await user_db.add(**new_user_data)
        chat = await chat_db.get_chat_user(msg.from_user.id)
        description = (
            f'Клієнт {new_user.full_name} авторизувався в боті. Карта клієнта {new_user.my_card}'
        )
        if chat:
            message = await chat.create_event_message(msg.bot, EventTypeEnum.AUTH, description=description, url=True)
            await msg.bot.pin_chat_message(chat_id=chat.chat_id, message_id=message.message_id)
        await payout_db.update_payout(payout.id, user_id=msg.from_user.id)

        #  Видаляємо дані юзера знайденого за номером телефону
        await user_db.delete_user(user_by_phone.user_id)
        await start_cmd(msg, user_db, chat_db, userbot, state, config)
        await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(start_cmd, CommandStart(), state='*')
    dp.register_message_handler(start_cmd, text=(Buttons.menu.back, Buttons.back.menu, Buttons.menu.dialog), state='*')
    dp.register_message_handler(authorization_cmd, text=Buttons.menu.auth)
    dp.register_message_handler(help_guide_cmd, state=AuthSG.Introduction, text=Buttons.menu.introduction)
    dp.register_message_handler(authorization_cmd, state=AuthSG.HelpGuide, text=Buttons.menu.introduction_2)
    dp.register_message_handler(search_user_cmd, state=AuthSG.Phone, content_types=ContentTypes.CONTACT)
    dp.register_message_handler(skip_authorization_cmd, state=AuthSG.Phone, text=Buttons.menu.skip)


async def create_user_dialog(msg: Message, chat_db: ChatRepo, userbot: UserbotController):
    chat, invite_link = await userbot.create_new_room(msg.from_user.full_name)
    await chat_db.add(chat_id=chat.id, invite_link=invite_link.invite_link, user_id=msg.from_user.id)
    chat_id = chat.id
    invite_link = invite_link.invite_link
    return chat_id, invite_link
