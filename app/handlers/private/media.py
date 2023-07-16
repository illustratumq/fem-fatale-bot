from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import MediaGroupFilter, Command
from aiogram.types import Message, ContentTypes

from app.database.services.repos import MediaRepo
from app.filters import IsAdminFilter


async def add_media_cmd(msg: Message, state: FSMContext):
    await state.update_data(media=[])
    await msg.answer('Додайте або перешліть усі медіа-файли, і натисніть /save')
    await state.set_state(state='media')


async def process_media_group_cmd(msg: Message, media: list[Message], state: FSMContext):
    try:
        data = await state.get_data()
        if data['media']:
            new_media = data['media']
            content_type = data['content_type']
        else:
            new_media = []
            content_type = media[0].content_type
        for message in media:
            if message.content_type != content_type:
                await msg.answer('Ви не можете додавати медіа різних типів разом (АБО фото АБО відео)')
                return
            else:
                new_media.append(message.photo[-1].file_id)
        await msg.answer(f'Матеріали додано ({len(media)}). Зберігти /save')
        await state.update_data(media=new_media, content_type=content_type)
    except:
        await msg.answer('Щоб додати групу фото або відео натисніть /add')


async def process_media_cmd(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        if data['media']:
            new_media = data['media']
            content_type = data['content_type']
        else:
            new_media = []
            content_type = msg.content_type
        if content_type != msg.content_type:
            await msg.answer('Ви не можете додавати медіа різних типів разом (АБО фото АБО відео)')
            return
        else:
            new_media.append(msg.photo[-1].file_id)
        await msg.answer('Матеріали додано (1). Зберігти /save')
        await state.update_data(media=new_media, content_type=content_type)
    except:
        await msg.answer('Щоб додати групу фото або відео натисніть /add')


async def save_media_cmd(msg: Message, media_db: MediaRepo, state: FSMContext):
    data = await state.get_data()
    if data['media']:
        media = await media_db.add(files=data['media'], content_type=data['content_type'].upper())
        name = f'Медіа група №{media.id}'
        await media_db.update_media(media.id, name=name)
        await msg.answer(f'Успішно завантажено {len(data["media"])} медіа-файлів. Назва пакунку: <b>{name}</b>')
        await state.finish()
    else:
        await msg.answer('Упс, щось пішло не так. Немає медіа для зберігання')
    del data['media']
    del data['content_type']
    await state.set_data(data)
    await state.finish()

def setup(dp: Dispatcher):
    dp.register_message_handler(add_media_cmd, IsAdminFilter(), Command('add'), state='*')
    dp.register_message_handler(
        process_media_group_cmd, IsAdminFilter(), MediaGroupFilter(True), content_types=ContentTypes.PHOTO,
        state='media')
    dp.register_message_handler(
        process_media_cmd, IsAdminFilter(), MediaGroupFilter(False), content_types=ContentTypes.PHOTO,
        state='media')
    dp.register_message_handler(save_media_cmd, IsAdminFilter(), Command('save'), state='media')

