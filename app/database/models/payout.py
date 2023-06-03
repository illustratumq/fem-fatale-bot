import sqlalchemy as sa
from babel.dates import format_datetime
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import PayoutTypeEnum


class Payout(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    photo_id = sa.Column(sa.VARCHAR(255), nullable=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    value = sa.Column(sa.INTEGER, nullable=False, default=0)
    user_answer = sa.Column(sa.VARCHAR(1000), nullable=False)
    description = sa.Column(sa.VARCHAR(1000), nullable=True)
    type = sa.Column(ENUM(PayoutTypeEnum), default=PayoutTypeEnum.MINUS, nullable=False)

    def construct_payout_text(self):
        types = {
            PayoutTypeEnum.MINUS: 'Списання балів',
            PayoutTypeEnum.PLUS: 'Нарахування балів'
        }
        return (
            f'Платіж: {types[self.type]}\n'
            f'Кількість: {self.value}\n'
            f'Коментар: {self.user_answer}\n'
            f'Дата: {format_datetime(self.created_at, locale="uk_UA")}'
        )
