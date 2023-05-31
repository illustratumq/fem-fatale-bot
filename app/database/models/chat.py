import sqlalchemy as sa

from app.database.models.base import TimedBaseModel


class Chat(TimedBaseModel):
    chat_id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True, nullable=True)
    event_id = sa.Column(sa.BIGINT, sa.ForeignKey('events.id', ondelete='SET NULL'), nullable=False)
    admin_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    active = sa.Column(sa.BOOLEAN, nullable=False, default=True)
