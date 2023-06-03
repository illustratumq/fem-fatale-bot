from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes

from app.database.services.enums import PayoutTypeEnum, UserStatusEnum
from app.database.services.repos import UserRepo, PayoutRepo
from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb
from app.states.states import AdminPayoutSG


async def admin_create_payout_cmd(msg: Message, state: FSMContext, user_db: UserRepo):
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
    await AdminPayoutSG.Payout.set()


async def save_payout_type(msg: Message, state: FSMContext):
    payout_type = 'minus' if msg.text == Buttons.admin.minus else 'plus'
    await state.update_data(payout_type=payout_type)
    action = {
        'minus': 'зняти з балансу',
        'plus': 'поповнити на баланс'
    }
    await msg.answer(f'Тепер оберіть скільки балів потібно {action[payout_type]}', reply_markup=basic_kb([Buttons.admin.back]))
    await AdminPayoutSG.Value.set()


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
        await AdminPayoutSG.Photo.set()


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
    await AdminPayoutSG.Confirm.set()


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
        if user.status == UserStatusEnum.ACTIVE:
            await user_db.update_user(user.user_id, status=UserStatusEnum.INACTIVE)
            await msg.answer('Схоже клієнт заблокував бота, і не отримає сповіщення')
    await msg.answer('Платіж створено успішно!', reply_markup=basic_kb([Buttons.admin.to_admin]))


def setup(dp: Dispatcher):
    dp.register_message_handler(
        admin_create_payout_cmd, IsAdminFilter(), text=Buttons.admin.create_payout_panel, state='select_action')
    dp.register_message_handler(save_payout_type, IsAdminFilter(), state=AdminPayoutSG.Payout)
    dp.register_message_handler(save_payout_value, IsAdminFilter(), state=AdminPayoutSG.Value)
    dp.register_message_handler(
        save_payout_photo, IsAdminFilter(), state=[AdminPayoutSG.Photo, AdminPayoutSG.Confirm],
        content_types=ContentTypes.PHOTO
    )
    dp.register_message_handler(
        confirm_payout_create, IsAdminFilter(), state=AdminPayoutSG.Photo, text=Buttons.admin.skip)
    dp.register_message_handler(
        create_payout, IsAdminFilter(), state=AdminPayoutSG.Confirm, text=Buttons.admin.done_payout)
    dp.register_message_handler(save_payout_comment, IsAdminFilter(), state=AdminPayoutSG.Confirm)