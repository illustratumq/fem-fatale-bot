import json
import logging
from typing import Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.services.repos import PartnerRepo

log = logging.getLogger(__name__)


class ExcelPartner:

    def __init__(self, index: str, data: dict):
        self.name = data['name'][index]
        self.phone = self.casting_phone_type(data['phone'][index])
        self.category = data['category'][index]
        self.address = data['address'][index]
        self.cashback = data['cashback'][index]
        self.city = data['city'][index]

    def to_json(self):
        data = dict(
            name=self.name, phone=self.phone, category=self.category,
            address=self.address, cashback=self.cashback
        )
        if self.city:
            data.update(city=self.city)
        return data

    @staticmethod
    def casting_phone_type(obj: Any):
        try:
            format_obj = str(obj).replace(' ', '').split('+')[-1].split('38')[-1]
            format_obj = f'38{format_obj}'
            return str(int(float(format_obj)))
        except ValueError:
            return None

    def __str__(self):
        return str(self.to_json())


class ExcelPartnerController:

    def __init__(self, path: str):
        self.path = path
        self.shape = 0

    def read(self):
        with open(self.path, mode='rb') as file:
            excel = pd.read_excel(file)
            data = json.loads(excel.to_json())
            self.shape = excel.shape[0]
        return [ExcelPartner(str(index), data) for index in range(self.shape)]

    async def add_partners_to_db(self, session: sessionmaker):
        session: AsyncSession = session()
        partner_db = PartnerRepo(session)
        for partner in self.read():
            await partner_db.add(**partner.to_json())
        log.info(f'Додано {self.shape} партнерів')
