import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from app.database.models.base import TimedBaseModel
from app.database.services.enums import ArticleStatusEnum


class Article(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    media_id = sa.Column(sa.BIGINT, sa.ForeignKey('medias.id', ondelete='SET NULL'), nullable=True)
    description = sa.Column(sa.VARCHAR(2000), nullable=True)
    title = sa.Column(sa.VARCHAR(200), nullable=True)
    status = sa.Column(ENUM(ArticleStatusEnum), default=ArticleStatusEnum.HIDE, nullable=False)
