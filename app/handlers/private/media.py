from aiogram import Dispatcher
from aiogram.dispatcher.filters import MediaGroupFilter
from aiogram.types import Message, ContentTypes

from app.database.services.repos import MediaRepo


async def save_media_group_cmd(msg: Message, media: list[Message], media_db: MediaRepo):
    media_files = [file.photo[-1].file_id for file in media]
    media_list = await media_db.add(files=media_files)
    name = media[0].text if media[0].text else f'Медіа група №{media_list.id}'
    await media_db.update_media(media_list.id, name=name)
    text = (
        f'Успішно завантажено {len(media)} фото.\n\n'
        f'👉 Скопіювати медіа ID: <code>{media_list.id}</code>'
    )
    await msg.reply(text)


async def save_photo_cmd(msg: Message, media_db: MediaRepo):
    media = await media_db.add(files=[msg.photo[-1].file_id])
    name = msg.text if msg.text else f'Медіа група №{media.id}'
    await media_db.update_media(media.id, name=name)
    await msg.reply(f'Ваше фото успішно завантажено.\n\n👉 Скопіювати медіа ID: <code>{media.id}</code>')


def setup(dp: Dispatcher):
    dp.register_message_handler(
        save_media_group_cmd, MediaGroupFilter(True), content_types=ContentTypes.PHOTO, state='*')
    dp.register_message_handler(save_photo_cmd, MediaGroupFilter(False), content_types=ContentTypes.PHOTO, state='*')

