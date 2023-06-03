import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import PayoutTypeEnum


class Payout(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    media_id = sa.Column(sa.BIGINT, sa.ForeignKey('medias.id', ondelete='SET NULL'), nullable=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    user_answer = sa.Column(sa.VARCHAR(1000), nullable=False)
    description = sa.Column(sa.VARCHAR(1000), nullable=True)
    type = sa.Column(ENUM(PayoutTypeEnum), default=PayoutTypeEnum.MINUS, nullable=False)
