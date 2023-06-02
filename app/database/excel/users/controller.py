import json
import logging
from typing import Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.services.enums import UserRoleEnum
from app.database.services.repos import UserRepo

log = logging.getLogger(__name__)


class ExcelUser:

    def __init__(self, index: str, data: dict):
        self.full_name = data['full_name'][index]
        self.phone = self.casting_phone_type(data['phone'][index])
        # self.second_phone = self.casting_phone_type(data['phone'][index])
        self.card = self.casting_integer_type(data['card'][index])
        self.balance = self.casting_integer_type(data['balance'][index], int)
        self.bankcard = self.casting_integer_type(data['bankcard'][index])
        self.role = data['type'][index]

    def to_json(self):
        roles = {
            'UserRoleEnum.ADMIN': UserRoleEnum.ADMIN,
            'UserRoleEnum.USER': UserRoleEnum.USER,
            'UserRoleEnum.PARTNER': UserRoleEnum.PARTNER,
            'UserRoleEnum.COMPETITION': UserRoleEnum.COMPETITION
        }
        return dict(
            full_name=self.full_name, phone=self.phone,
            card=self.card, balance=self.balance, bankcard=self.bankcard, role=roles[self.role]
        )

    @staticmethod
    def casting_phone_type(obj: Any):
        try:
            format_obj = str(obj).replace(' ', '').split('+')[-1].split('38')[-1]
            format_obj = f'38{format_obj}'
            return str(int(float(format_obj)))
        except ValueError:
            return None

    @staticmethod
    def casting_integer_type(obj: Any, typing: type = str):
        try:
            obj = int(float(str(obj).replace(' ', '')))
            return typing(obj)
        except ValueError:
            return None

    def __str__(self):
        return str(self.to_json())


class ExcelUserController:

    def __init__(self, path: str):
        self.path = path
        self.shape = 0

    def read(self):
        with open(self.path, mode='rb') as file:
            excel = pd.read_excel(file)
            data = json.loads(excel.to_json())
            self.shape = excel.shape[0]
        return [ExcelUser(str(index), data) for index in range(self.shape)]

    async def add_users_to_db(self, session: sessionmaker):
        session: AsyncSession = session()
        user_db = UserRepo(session)
        for user in self.read():
            await user_db.add(**user.to_json(), user_id=int(user.phone))
        log.info(f'Додано {self.shape} користувачів')
