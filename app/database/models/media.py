import sqlalchemy as sa

from app.database.models.base import TimedBaseModel


class Media(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    files = sa.Column(sa.ARRAY(sa.VARCHAR), nullable=False)
