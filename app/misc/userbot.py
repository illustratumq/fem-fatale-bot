import logging
import os
from datetime import timedelta

from pyrogram import Client
from pyrogram.errors import ChatIdInvalid
from pyrogram.raw.core import TLObject
from pyrogram.raw.functions.messages import EditChatAdmin, DeleteChat
from pyrogram.types import Chat, ChatInviteLink, ChatPermissions, ChatMember

from app.config import Config
from app.misc.photo import make_chat_photo
from app.misc.times import now


log = logging.getLogger(__name__)


class UserbotController:
    def __init__(self, config: Config, bot_username: str):
        try:
            self._client = Client(config.userbot.session_name, no_updates=True)
        except AttributeError:
            self._client = Client(config.userbot.session_name, config.userbot.api_id, config.userbot.api_hash,
                                  no_updates=True)
        self._bot_username = bot_username
        self.config = config

    async def get_client_user_id(self) -> int:
        async with self._client:
            return (await self._client.get_me()).id

    async def clean_chat_history(self, chat_id: int):
        async with self._client as client:
            history = client.get_chat_history(chat_id=chat_id)
            message_ids = []
            async for msg in history:
                message_ids.append(msg.id)
            await client.delete_messages(chat_id=chat_id, message_ids=message_ids)

    async def get_chat_members(self, chat_id: int) -> list:
        members = []
        async with self._client as client:
            async for member in client.get_chat_members(chat_id):
                member: ChatMember
                members.append(member.user.id)
        return members

    async def create_new_room(self, room_name: str) -> tuple[Chat, ChatInviteLink]:
        async with self._client as client:
            chat = await self._create_group(client, room_name)
            await self._set_chat_photo(chat, room_name)
            await self._set_chat_permissions(client, chat)
            await self._set_bot_admin(client, chat)
            for admin_id in self.config.bot.admin_ids:
                try:
                    await self.add_chat_member(chat.id, admin_id)
                except Exception as error:
                    log.error(error)
            invite_link = await self._create_invite_link(client, chat)
        return chat, invite_link

    async def _create_group(self, client: Client, room_name: str) -> Chat:
        group = await client.create_group(room_name, [self._bot_username])
        return group

    @staticmethod
    async def _set_chat_permissions(client: Client, chat: Chat) -> None:
        permissions = ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True,
            can_send_polls=False, can_add_web_page_previews=False, can_change_info=False,
            can_invite_users=False, can_pin_messages=True,
        )
        await client.set_chat_permissions(chat.id, permissions)

    @staticmethod
    async def _set_chat_photo(chat: Chat, room_name: str) -> None:
        new_photo_path = make_chat_photo(room_name)
        await chat.set_photo(photo=new_photo_path)
        os.remove(new_photo_path)

    @staticmethod
    async def _create_invite_link(client: Client, chat: Chat) -> ChatInviteLink:
        return await client.create_chat_invite_link(chat.id, name='For join requests', creates_join_request=True)

    @staticmethod
    async def _invoke(client: Client, raw_function: TLObject) -> None:
        await client.invoke(raw_function)

    async def _set_bot_admin(self, client: Client, chat: Chat) -> None:
        raw = EditChatAdmin(chat_id=chat.id, user_id=await client.resolve_peer(self._bot_username), is_admin=True)
        try:
            await self._invoke(client, raw)
        except ChatIdInvalid:
            raw.chat_id = -chat.id
            await self._invoke(client, raw)

    async def add_chat_member(self, chat_id: int, user_id: int):
        async with self._client as client:
            client: Client
            await client.add_chat_members(chat_id=chat_id, user_ids=user_id)

    async def kick_chat_member(self, chat_id: int, user_id: int):
        async with self._client as client:
            client: Client
            await client.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=now() + timedelta(seconds=5))

    async def _delete_group(self, client: Client, chat: Chat) -> None:
        raw = DeleteChat(chat_id=chat.id)
        try:
            await self._invoke(client, raw)
        except ChatIdInvalid:
            raw.chat_id = -chat.id
            await self._invoke(client, raw)
