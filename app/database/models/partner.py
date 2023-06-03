import sqlalchemy as sa

from app.database.models.base import TimedBaseModel


class Partner(TimedBaseModel):
    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    media_id = sa.Column(sa.BIGINT, sa.ForeignKey('medias.id', ondelete='SET NULL'), nullable=True)
    name = sa.Column(sa.VARCHAR(100), nullable=False)
    category = sa.Column(sa.VARCHAR(20), nullable=False)
    address = sa.Column(sa.VARCHAR(500), nullable=False)
    cashback = sa.Column(sa.VARCHAR(50), nullable=True)
    phone = sa.Column(sa.VARCHAR(12), nullable=True)
    city = sa.Column(sa.VARCHAR(20), nullable=True, default='Київ')
    description = sa.Column(sa.VARCHAR(1000), nullable=True)
    priority = sa.Column(sa.INTEGER, nullable=True)

