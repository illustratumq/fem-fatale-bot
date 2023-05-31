from enum import Enum


class UserStatusEnum(Enum):
    ACTIVE = 'ACTIVE'
    UNAUTHORIZED = 'UNAUTHORIZED'


class UserRoleEnum(Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    MODERATOR = 'MODERATOR'
    COMPETITION = 'COMPETITION'


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
    HELP = 'HELP'
