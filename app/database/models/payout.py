from datetime import datetime

import sqlalchemy as sa
from babel.dates import format_datetime
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import PayoutTypeEnum


class Payout(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    media_id = sa.Column(sa.BIGINT, sa.ForeignKey('medias.id', ondelete='SET NULL'), nullable=True)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    partner_id = sa.Column(sa.BIGINT, sa.ForeignKey('partners.id', ondelete='SET NULL'), nullable=True)
    payout_date = sa.Column(sa.DateTime, default=datetime.now(), nullable=True)
    price = sa.Column(sa.INTEGER, nullable=False, default=0)
    general_price = sa.Column(sa.INTEGER, nullable=False, default=0)
    service_price = sa.Column(sa.INTEGER, nullable=False, default=0)
    user_price = sa.Column(sa.INTEGER, nullable=False, default=0)
    general_percent = sa.Column(sa.INTEGER, nullable=False, default=0)
    service_percent = sa.Column(sa.INTEGER, nullable=False, default=0)
    user_percent = sa.Column(sa.INTEGER, nullable=False, default=0)
    comment = sa.Column(sa.VARCHAR(1000), nullable=True)
    description = sa.Column(sa.VARCHAR(1000), nullable=True)
    type = sa.Column(ENUM(PayoutTypeEnum), default=PayoutTypeEnum.MINUS, nullable=False)
    tag = sa.Column(sa.VARCHAR(15), nullable=False, default='edited')

    async def construct_payout_text(self, partner_db):
        types = {
            PayoutTypeEnum.MINUS: 'Списання {} балів',
            PayoutTypeEnum.PLUS: 'Нарахування {} балів'
        }
        text = f'{types[self.type].format(self.user_price)}\n'
        if self.partner_id:
            partner = await partner_db.get_partner(self.partner_id)
            text += f'Заклад: {partner.name}\n'
        if self.comment:
            text += f'Коментар:\n\n{self.comment}'
        text += f'Дата: {format_datetime(self.created_at, locale="uk_UA")}'
        return text
