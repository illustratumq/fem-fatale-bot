from enum import Enum


class UserStatusEnum(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    UNAUTHORIZED = 'UNAUTHORIZED'


class UserRoleEnum(Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    MODERATOR = 'MODERATOR'
    COMPETITION = 'COMPETITION'
    PARTNER = 'PARTNER'


class ArticleStatusEnum(Enum):
    ACTIVE = 'ACTIVE'
    HIDE = 'HIDE'


class EventStatusEnum(Enum):
    ACTIVE = 'ACTIVE'
    PROCESSED = 'PROCESSED'
    DONE = 'DONE'


class EventTypeEnum(Enum):
    RESERV = 'RESERV'
    PAYOUT = 'PAYOUT'
    AUTH = 'AUTH'
    HELP = 'HELP'


class PayoutTypeEnum(Enum):
    MINUS = 'MINUS'
    PLUS = 'PLUS'


class ContentTypeEnum(Enum):
    VIDEO = 'VIDEO'
    PHOTO = 'PHOTO'
