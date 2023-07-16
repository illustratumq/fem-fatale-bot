from aiogram import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ContentTypes, ChatType, ChatJoinRequest

from app.config import Config
from app.database.services.enums import UserRoleEnum
from app.database.services.repos import ChatRepo, UserRepo
from app.filters.admin import IsDialogMessage


async def dialog_from_user_cmd(msg: Message, chat_db: ChatRepo, config: Config):
    if not msg.from_user.is_bot and msg.from_user.id not in config.bot.admin_ids:
        chat = await chat_db.get_chat_user(msg.from_user.id)
        await msg.bot.copy_message(
            chat_id=chat.chat_id, from_chat_id=msg.from_user.id, message_id=msg.message_id
        )

async def dialog_from_admin_cmd(msg: Message, chat_db: ChatRepo, user_db: UserRepo):
    if not msg.from_user.is_bot:
        chat = await chat_db.get_chat(msg.chat.id)
        admin = await user_db.get_user(msg.from_user.id)
        if admin:
            if admin.role == UserRoleEnum.ADMIN:
                await msg.bot.copy_message(
                    chat_id=chat.user_id, from_chat_id=msg.chat.id, message_id=msg.message_id,
                    # reply_markup=basic_kb([Buttons.menu.back])
                )
            else:
                await msg.reply('Упс... Схоже ви не є адміністратором')
        else:
            await msg.reply(f'Упс... {msg.from_user.full_name}, '
                            f'ви ще не зареєстровані в боті. Зробіть це зараз: @{(await msg.bot.me).username}')


async def process_chat_join_request(cjr: ChatJoinRequest, user_db: UserRepo):
    admin = await user_db.get_user(cjr.from_user.id)
    if admin.role == UserRoleEnum.ADMIN:
        await cjr.approve()
    else:
        await cjr.decline()
        await cjr.bot.send_message(cjr.from_user.id, text='Ви не є адміністратором сервісу')


def setup(dp: Dispatcher):
    dp.register_chat_join_request_handler(process_chat_join_request, state='*')
    dp.register_message_handler(dialog_from_user_cmd, ChatTypeFilter(ChatType.PRIVATE), IsDialogMessage(),
                                content_types=ContentTypes.ANY, state='*')
    dp.register_message_handler(dialog_from_admin_cmd, ChatTypeFilter(ChatType.GROUP), IsDialogMessage(),
                                content_types=ContentTypes.ANY, state='*')
