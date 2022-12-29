from sqlalchemy import UniqueConstraint

from db import db


class MarketMessage(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    message = db.Column('message', db.TEXT, nullable=False)
    sale_id = db.Column('sale_id', db.INT, nullable=False)
    item_id = db.Column('item_id', db.INT, nullable=False)
    user_id = db.Column('user_id', db.INT, nullable=False)
    message_type = db.Column('message_type', db.TEXT, nullable=False)
    channel_id = db.Column('channel_id', db.TEXT, nullable=False)
    activit_type = db.Column('activit_type', db.TEXT, nullable=False)
    message_date = db.Column('message_date', db.TIMESTAMP, nullable=False)

    __tablename__ = 'market_message'
    __table_args__ = (
        UniqueConstraint('sale_id'),
    )

    def __repr__(self):
        return '<MarketMessage %r>' % self.id
