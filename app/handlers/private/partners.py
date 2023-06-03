from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, MediaGroup, InputMediaPhoto

from app.database.services.repos import PartnerRepo, MediaRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb
from app.states.states import PartnerSG


def chunk_list(lst, chunk_size):
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]


async def partners_cmd(msg: Message, partner_db: PartnerRepo):
    categories_all = [partner.category for partner in await partner_db.get_all()]
    categories = list(set(categories_all))
    categories.sort(key=lambda c: categories_all.count(c), reverse=True)
    await msg.answer('Будь ласка оберіть категорію закладів, які бажаєте переглянути',
                     reply_markup=basic_kb(chunk_list(categories, 2) + [[Buttons.menu.back]]))
    await PartnerSG.Categories.set()


async def save_category_name(msg: Message, partner_db: PartnerRepo, media_db: MediaRepo, state: FSMContext):
    partners = await partner_db.get_partners_category(msg.text)
    if partners:
        await state.update_data(category=msg.text)
        cities = list(set([partner.city for partner in partners]))
        if len(cities) > 1:
            pass # TODO city
        else:
            await state.update_data(city=cities[0], page=0)
            await partner_pagination_cmd(msg, partner_db, media_db, state)
    else:
        await msg.answer('Такої категорії немає. Будь-ласка спробуйте ще раз')


async def partner_pagination_cmd(msg: Message, partner_db: PartnerRepo, media_db: MediaRepo, state: FSMContext):
    data = await state.get_data()
    if not data.items():
        await partners_cmd(msg, partner_db)
        return
    city = data['city']
    page = data['page']
    category = data['category']
    partners = chunk_list(await partner_db.get_partners_category(category, city), 6)

    if msg.text == Buttons.partners.next:
        page = (page + 1) % len(partners)
    elif msg.text == Buttons.partners.prev:
        page = (page - 1) % len(partners)
    elif partner := await partner_db.get_partner_name(msg.text):
        await partner_view_cmd(msg, partner, media_db)
        return

    partners = partners[page]
    text = (
        f'{category} в місті {city}\n\n'
        f'{partners_list_text(partners, page)}\n'
        f'Обери заклад, або гортай сторінку 👇'
    )
    reply_markup = basic_kb(
        chunk_list([partner.name for partner in partners], 2) +
        [[Buttons.partners.prev, Buttons.back.categories, Buttons.partners.next]]
    )
    message = await msg.answer(text, reply_markup=reply_markup)
    await state.update_data(page=page, last_msg_id=message.message_id)
    await PartnerSG.Pagination.set()


async def partner_view_cmd(msg: Message, partner: PartnerRepo.model, media_db: MediaRepo):
    text = (
        f'Категорія: {partner.category}\n'
        f'Назва закладу: {partner.name}\n'
        f'Кешбек: {partner.cashback}%\n'
        f'🗺 Адреса - {partner.city}, {partner.address}\n'
        f'☎ Телефон - {partner.phone}\n\n'
    )
    reply_markup = basic_kb([[Buttons.menu.reserv], [Buttons.back.partners]])
    if partner.description:
        text += partner.description
    if partner.media_id:
        media = await media_db.get_media(partner.media_id)
        if len(media.files) > 1:
            data = dict(caption=text)
            await msg.answer(partner.name, reply_markup=reply_markup)
            group = MediaGroup([InputMediaPhoto(file, **(data if media.files[-1] == file else {})) for file in media.files])
            await msg.answer_media_group(group)
        else:
            await msg.answer_photo(media.files[0], caption=text, reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)


def setup(dp: Dispatcher):
    dp.register_message_handler(partners_cmd, text=(Buttons.menu.partners, Buttons.back.categories), state='*')
    dp.register_message_handler(save_category_name, state=PartnerSG.Categories)
    dp.register_message_handler(partner_pagination_cmd, state=PartnerSG.Pagination)


def partners_list_text(partners: list[PartnerRepo.model], page: int):
    text = ''
    start = 6 * page + 1
    end = len(partners) + start
    for partner, num in zip(partners, range(start, end)):
        text += f'{num}. {partner.name}\n'
    return text


async def clear_last_msg(msg: Message, state: FSMContext):
    data = await state.get_data()
    if 'last_msg_id' in data.keys():
        await msg.bot.delete_message(msg.from_user.id, data['last_msg_id'])
