import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode, AllowedUpdates
from sqlalchemy.orm import sessionmaker

from app import middlewares, handlers
from app.config import Config
from app.database.excel.partners.controller import ExcelPartnerController
from app.database.excel.users.controller import ExcelUserController
from app.database.services.db_engine import create_db_engine_and_session_pool
from app.misc.userbot import UserbotController

log = logging.getLogger(__name__)


async def setup_excel_data(session: sessionmaker):
    await ExcelUserController('app/database/excel/users/users.xlsx').add_users_to_db(session)
    await ExcelPartnerController('app/database/excel/partners/partners.xlsx').add_partners_to_db(session)


async def main():
    config = Config.from_env()
    bl.basic_colorized_config(level=config.misc.log_level)
    log.info('Бот запущенно...')

    storage = RedisStorage2(host=config.redis.host, port=config.redis.port)
    bot = Bot(config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)
    db_engine, sqlalchemy_session_pool = await create_db_engine_and_session_pool(
        config.db.sqlalchemy_url
    )
    userbot = UserbotController(config, (await bot.me).username)

    environments = dict(bot=bot, config=config, dp=dp, userbot=userbot)

    middlewares.setup(dp, sqlalchemy_session_pool, environments)
    handlers.setup(dp)

    allowed_updates = (
        AllowedUpdates.MESSAGE + AllowedUpdates.CALLBACK_QUERY + AllowedUpdates.CHAT_JOIN_REQUEST
    )

    if config.misc.reset_db:
        await setup_excel_data(sqlalchemy_session_pool)

    try:
        await dp.skip_updates()
        await dp.start_polling(allowed_updates=allowed_updates, reset_webhook=True)
    finally:
        await storage.close()
        await storage.wait_closed()
        await (await bot.get_session()).close()
        await db_engine.dispose()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.warning('Бот зупинено')
