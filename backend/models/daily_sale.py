from sqlalchemy import func, UniqueConstraint

from db import db


class DailySale(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    type = db.Column('type', db.TEXT, nullable=False)
    type_id = db.Column('type_id', db.INT, nullable=False)
    sale_at = db.Column('sale_at', db.TIMESTAMP, server_default=func.now())
    sale_from = db.Column('sale_from', db.TEXT, nullable=False)
    currency = db.Column('currency', db.TEXT, nullable=True)
    price = db.Column('price', db.INT, nullable=True)

    __tablename__ = 'daily_sale'
    __table_args__ = (
        UniqueConstraint('type', 'type_id', 'sale_at', 'sale_from', name='uq_daily_sale'),
    )

    def __repr__(self):
        return '<DailySale %r>' % self.id
