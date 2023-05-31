import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import EventStatusEnum, EventTypeEnum


class Event(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    admin_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    chat_id = sa.Column(sa.BIGINT, sa.ForeignKey('chats.chat_id', ondelete='SET NULL'), nullable=False)
    message_id = sa.Column(sa.BIGINT, nullable=True)
    title = sa.Column(sa.VARCHAR(100), nullable=True)
    description = sa.Column(sa.VARCHAR(500), nullable=True)
    url = sa.Column(sa.VARCHAR(255), nullable=True)
    status = sa.Column(ENUM(EventStatusEnum), nullable=True, default=EventStatusEnum.ACTIVE)
    help = sa.Column(ENUM(EventStatusEnum), nullable=True, default=EventTypeEnum.HELP)
