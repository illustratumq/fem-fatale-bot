from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes, ReplyKeyboardRemove

from app.config import Config
from app.database.services.repos import ChatRepo, UserRepo, EventRepo
from app.filters import IsAdminFilter
from app.filters.admin import ConnectionNode
from app.handlers.admin.event import event_processing_back
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb, menu_kb


async def create_chat(msg: Message, user_db: UserRepo, chat_db: ChatRepo, state: FSMContext):
    data = await state.get_data()
    user = await user_db.get_user(data['user_id'])
    chat = await chat_db.add(user_id=data['user_id'], admin_id=msg.from_user.id)
    await state.update_data(chat_id=chat.chat_id)
    to_admin_text = (
        '💬 Ви знаходитесь в режимі спілкування, всі ваші повідомлення будуть транслюватись ботом користувачу.\n\n'
        'Для того, щоб завершити спілкування, будь ласка використовуйте кнопки нижче.\n\n'
        f'#Чат_номер_{chat.chat_id}.'
    )
    to_user_text = (
        f'💬 Вітаю {user.first_name}, на ваше повідомлення відповість менеджер ФемФаталь\n\n'
        f'Якщо ви бажаєте завершити діалог, будь ласка скористайтеся кнопкою нижче'
    )
    await msg.answer(to_admin_text, reply_markup=basic_kb([Buttons.admin.cancel_chat]))
    await msg.bot.send_message(user.user_id, to_user_text, reply_markup=ReplyKeyboardRemove())


async def connection_node(msg: Message, user_db: UserRepo, chat_db: ChatRepo):
    if await chat_db.get_chat_admin(msg.from_user.id):
        admin = await user_db.get_user(msg.from_user.id)
        chat = await chat_db.get_chat_admin(admin.user_id)
        await msg.bot.copy_message(chat.user_id, msg.from_user.id, msg.message_id)
    else:
        user = await user_db.get_user(msg.from_user.id)
        chat = await chat_db.get_chat_user(user.user_id)
        await msg.bot.copy_message(chat.admin_id, msg.from_user.id, msg.message_id)


async def cancel_chat_node_confirm(msg: Message, state: FSMContext):
    await msg.answer('Підтвердіть своє рішення, натисність на кнопку ще раз',
                     reply_markup=basic_kb([[Buttons.admin.cancel_chat], [Buttons.admin.cancel]]))
    await state.set_state(state='confirm_cancel')


async def keep_chatting_node(msg: Message, state: FSMContext):
    await msg.answer('Дія відмінена, продовжуей діалог!', reply_markup=basic_kb([Buttons.admin.cancel_chat]))
    await state.finish()


async def cancel_chat_node(msg: Message, chat_db: ChatRepo, user_db: UserRepo, event_db: EventRepo, config: Config,
                           state: FSMContext):
    chat = await chat_db.get_chat_admin(msg.from_user.id)
    user = await user_db.get_user(chat.user_id)
    await chat_db.update_chat(chat.chat_id, active=False)
    await msg.bot.send_message(chat.user_id, 'Ваша розмова була завершена менеджером',
                               reply_markup=menu_kb(user.is_authorized))
    await msg.answer('Розмова було успішно завершена')
    if chat.event_id:
        await state.update_data(event_id=chat.event_id, user_id=user.user_id)
        await event_processing_back(msg, user_db, event_db, config, state)


def setup(dp: Dispatcher):
    dp.register_message_handler(
        create_chat, IsAdminFilter(), text=Buttons.admin.create_chat_panel, state='select_action')

    dp.register_message_handler(
        cancel_chat_node, ConnectionNode(), state='confirm_cancel', text=Buttons.admin.cancel_chat)
    dp.register_message_handler(
        cancel_chat_node_confirm, ConnectionNode(), state='*', text=Buttons.admin.cancel_chat)
    dp.register_message_handler(
        keep_chatting_node, ConnectionNode(), state='confirm_cancel', text=Buttons.admin.cancel)

    dp.register_message_handler(connection_node, ConnectionNode(), state='*')
    dp.register_message_handler(connection_node, ConnectionNode(), state='*', content_types=ContentTypes.PHOTO)
    dp.register_message_handler(connection_node, ConnectionNode(), state='*', content_types=ContentTypes.DOCUMENT)
    dp.register_message_handler(connection_node, ConnectionNode(), state='*', content_types=ContentTypes.VIDEO)
