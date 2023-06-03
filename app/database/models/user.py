from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
import sqlalchemy as sa

from app.database.services.enums import UserStatusEnum, UserRoleEnum


class User(TimedBaseModel):
    user_id = sa.Column(sa.BIGINT(), primary_key=True, autoincrement=False, index=True)
    full_name = sa.Column(sa.VARCHAR(255), nullable=False)
    status = sa.Column(ENUM(UserStatusEnum), nullable=False, default=UserStatusEnum.UNAUTHORIZED)
    role = sa.Column(ENUM(UserRoleEnum), nullable=False, default=UserRoleEnum.USER)
    phone = sa.Column(sa.VARCHAR(12), nullable=True)
    card = sa.Column(sa.VARCHAR(10), nullable=True)
    bankcard = sa.Column(sa.VARCHAR(16), nullable=True)
    balance = sa.Column(sa.BIGINT, nullable=False, default=0)
    info = sa.Column(sa.VARCHAR(1000), nullable=True)

    @property
    def first_name(self):
        return self.full_name.split(' ')[0]

    @property
    def is_authorized(self):
        return self.status != UserStatusEnum.UNAUTHORIZED

    @property
    def my_card(self):
        return '0' * (4 - len(self.card)) + self.card
