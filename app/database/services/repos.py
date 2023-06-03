import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.models import *
from app.database.services.db_ctx import BaseRepo
from app.database.services.enums import UserStatusEnum, ArticleStatusEnum


class UserRepo(BaseRepo[User]):
    model = User

    async def get_user(self, user_id: int) -> User:
        return await self.get_one(self.model.user_id == user_id)

    async def get_user_phone(self, phone: str) -> User:
        return await self.get_one(self.model.phone == phone)

    async def get_user_card(self, card: str) -> User:
        return await self.get_one(self.model.card == card)

    async def get_user_status(self, status: UserStatusEnum) -> list[User]:
        return await self.get_all(self.model.status == status)

    async def get_user_name(self, full_name: str) -> User:
        return await self.get_one(self.model.full_name == full_name)

    async def update_user(self, user_id: int, **kwargs) -> None:
        return await self.update(self.model.user_id == user_id, **kwargs)

    async def generate_user_card(self, user_id: int):
        existing_cards = [u.card for u in await self.get_all() if u.card]
        all_cards = set([str(i) for i in range(1, 10000)])
        free_cards = all_cards - set(existing_cards)
        card = random.choice(list(free_cards))
        await self.update_user(user_id, card=str(card))
        return card

    async def delete_user(self, user_id: int):
        return await self.delete(self.model.user_id == user_id)


class PartnerRepo(BaseRepo[Partner]):
    model = Partner

    async def get_partner(self, partner_id: int) -> Partner:
        return await self.get_one(self.model.id == partner_id)

    async def get_partner_name(self, name: str) -> Partner:
        return await self.get_one(self.model.name == name)

    async def get_partners_category(self, category: str, city: str = None) -> list[Partner]:
        if city:
            return await self.get_all(self.model.category == category, self.model.city == city)
        else:
            return await self.get_all(self.model.category == category)

    async def update_partner(self, partner_id: int, **kwargs) -> None:
        return await self.update(self.model.id == partner_id, **kwargs)


class ChatRepo(BaseRepo[Chat]):
    model = Chat

    async def get_chat(self, chat_id: int) -> Chat:
        return await self.get_one(self.model.chat_id == chat_id)

    async def get_chat_user(self, user_id: int) -> Chat:
        return await self.get_one(self.model.user_id == user_id, self.model.active == True)

    async def get_chat_admin(self, admin_id: int) -> Chat:
        return await self.get_one(self.model.admin_id == admin_id, self.model.active == True)

    async def update_chat(self, chat_id: int, **kwargs) -> None:
        return await self.update(self.model.chat_id == chat_id, **kwargs)

    async def delete_chat(self, chat_id: int):
        return await self.delete(self.model.chat_id == chat_id)


class ArticleRepo(BaseRepo[Article]):
    model = Article

    async def get_article(self, article_id: int) -> Article:
        return await self.get_one(self.model.id == article_id)

    async def get_article_status(self, status: ArticleStatusEnum | str) -> list[Article]:
        if status == '*':
            return await self.get_all()
        else:
            return await self.get_all(self.model.status == status)

    async def update_article(self, article_id: int, **kwargs) -> None:
        return await self.update(self.model.id == article_id, **kwargs)

    async def delete_article(self, article_id: int):
        return await self.delete(self.model.id == article_id)


class EventRepo(BaseRepo[Event]):
    model = Event

    async def get_event(self, event_id: int) -> Event:
        return await self.get_one(self.model.id == event_id)

    async def update_event(self, event_id: int, **kwargs) -> None:
        return await self.update(self.model.id == event_id, **kwargs)

    async def delete_event(self, event_id: int):
        return await self.delete(self.model.id == event_id)


class MediaRepo(BaseRepo[Media]):
    model = Media

    async def get_media(self, media_id: int) -> Media:
        return await self.get_one(self.model.id == media_id)

    async def update_media(self, media_id: int, **kwargs) -> None:
        return await self.update(self.model.id == media_id, **kwargs)

    async def delete_media(self, media_id: int):
        return await self.delete(self.model.id == media_id)


class PayoutRepo(BaseRepo[Payout]):
    model = Payout

    async def get_payout(self, payout_id: int) -> Payout:
        return await self.get_one(self.model.id == payout_id)

    async def update_payout(self, payout_id: int, **kwargs) -> None:
        return await self.update(self.model.id == payout_id, **kwargs)

    async def delete_payout(self, payout_id: int):
        return await self.delete(self.model.id == payout_id)


class DatabaseRepo:

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def user_db(self):
        return UserRepo(self.session)

    @property
    def partner_db(self):
        return PartnerRepo(self.session)

    @property
    def chat_db(self):
        return ChatRepo(self.session)

    @property
    def event_db(self):
        return EventRepo(self.session)

    @property
    def media_db(self):
        return MediaRepo(self.session)
