import sqlalchemy as sa
from aiogram.types import MediaGroup, InputMediaPhoto, InputMediaVideo
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import ContentTypeEnum


class Media(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    name = sa.Column(sa.VARCHAR(20), nullable=True)
    files = sa.Column(sa.ARRAY(sa.VARCHAR), nullable=False)
    content_type = sa.Column(ENUM(ContentTypeEnum), default=ContentTypeEnum.PHOTO, nullable=False)

    def is_media_group(self):
        return len(self.files) > 1

    def get_media_group(self, caption: str, **kwargs):
        data = dict(caption=caption)
        data.update(**kwargs)
        input_media = InputMediaPhoto if self.content_type == ContentTypeEnum.PHOTO else InputMediaVideo
        return MediaGroup([input_media(file, **(data if self.files[-1] == file else {})) for file in self.files])
