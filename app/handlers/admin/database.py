import pandas as pd
from aiogram import Dispatcher
from aiogram.types import Message, InputFile

from app.database.services.repos import UserRepo, PartnerRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb


def update_dataframe(frame: dict, model: dict):
    keys = list(frame.keys())
    for k, v in model.items():
        if k in keys:
            value = str(v) if v else ''
            frame.get(k).append(value)


async def select_database_type(msg: Message):
    await msg.answer('Оберіть базу даних',
                     reply_markup=basic_kb([[Buttons.admin.database_clients, Buttons.admin.database_partners],
                                            [Buttons.admin.to_admin]]))


async def download_user_db(msg: Message, user_db: UserRepo):
    await msg.bot.send_chat_action(msg.from_user.id, 'upload_document')
    dataframe = {}
    keys = [
        'user_id', 'full_name', 'phone',
        'card', 'bankcard', 'role', 'balance', 'status'
    ]
    for key in keys:
        dataframe.update({key: []})
    for user in await user_db.get_all():
        update_dataframe(dataframe, user.__dict__)
    df = pd.DataFrame(dataframe)
    path_name = 'app/database/excel/users/users_remastered.xlsx'
    df.to_excel(path_name)
    await msg.reply_document(document=InputFile(path_name),
                             caption=f'Готово! Записно {len(dataframe.get("user_id"))} клієнтів.')
    # os.remove(path_name)


async def download_partner_db(msg: Message, partner_db: PartnerRepo):
    await msg.bot.send_chat_action(msg.from_user.id, 'upload_document')
    dataframe = {}
    keys = [
        'category',
        'city', 'name', 'address', 'cashback',
        'phone', 'description'
    ]
    for key in keys:
        dataframe.update({key: []})
    for partner in await partner_db.get_all():
        update_dataframe(dataframe, partner.__dict__)
    df = pd.DataFrame(dataframe)
    path_name = 'app/database/excel/partners/partners_remastered.xlsx'
    df.to_excel(path_name)
    await msg.reply_document(document=InputFile(path_name),
                             caption=f'Готово! Записно {len(dataframe.get("name"))} партнерів.')
    # os.remove(path_name)


def setup(dp: Dispatcher):
    dp.register_message_handler(select_database_type, IsAdminFilter(), text=Buttons.admin.database, state='*')
    dp.register_message_handler(download_user_db, IsAdminFilter(), text=Buttons.admin.database_clients, state='*')
    dp.register_message_handler(download_partner_db, IsAdminFilter(), text=Buttons.admin.database_partners, state='*')