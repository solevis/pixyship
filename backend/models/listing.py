from db import db


class Listing(db.Model):
    id = db.Column("id", db.INT, primary_key=True)
    sale_at = db.Column("sale_at", db.TIMESTAMP, nullable=False)
    item_name = db.Column("item_name", db.TEXT, nullable=False)
    item_id = db.Column("item_id", db.INT, nullable=False)
    amount = db.Column("amount", db.INT, nullable=False)
    currency = db.Column("currency", db.TEXT, nullable=False)
    price = db.Column("price", db.INT, nullable=False)
    user_id = db.Column("user_id", db.INT, nullable=False)
    user_name = db.Column("user_name", db.TEXT, nullable=False)
    seller_id = db.Column("seller_id", db.INT, nullable=False)
    seller_name = db.Column("seller_name", db.TEXT, nullable=False)
