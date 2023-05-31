import logging
from dataclasses import dataclass

from environs import Env
from sqlalchemy.engine import URL


@dataclass
class TgBot:
    token: str
    name: str
    admin_ids: tuple[int]


@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def sqlalchemy_url(self) -> str:
        return str(URL.create(
            'postgresql+asyncpg',
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        ))


@dataclass
class RedisConfig:
    host: str
    port: int


@dataclass
class Miscellaneous:
    log_level: str
    timezone: str


@dataclass
class Config:
    bot: TgBot
    db: DbConfig
    redis: RedisConfig
    misc: Miscellaneous

    @classmethod
    def from_env(cls, path: str = None) -> 'Config':
        env = Env()
        env.read_env(path)

        return Config(
            bot=TgBot(
                token=env.str('BOT_TOKEN'),
                admin_ids=tuple(map(int, env.list('ADMIN_IDS'))),
                name=env.str('BOT_NAME')
            ),
            db=DbConfig(
                host=env.str('DB_HOST', 'localhost'),
                port=env.int('DB_PORT', 5432),
                user=env.str('DB_USER', 'postgres'),
                password=env.str('DB_PASS', 'postgres'),
                database=env.str('DB_NAME', 'postgres')
            ),
            redis=RedisConfig(
                host=env.str('REDIS_HOST', 'localhost'),
                port=env.int('REDIS_PORT', 6379)
            ),
            misc=Miscellaneous(
                log_level=env.str('LOG_LEVEL', logging.INFO),
                timezone=env.str('TIMEZONE', 'Europe/Kiev')
            )
        )
