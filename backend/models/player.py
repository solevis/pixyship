from db import db


class Player(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    name = db.Column('name', db.TEXT, nullable=False)
    trophies = db.Column('trophies', db.INT, nullable=False)
    alliance_id = db.Column('alliance_id', db.INT)
    last_login_at = db.Column('last_login_at', db.TIMESTAMP)

    def __repr__(self):
        return '<User %r>' % self.name
