from db import db


class Alliance(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    name = db.Column('name', db.TEXT, nullable=False)
    sprite_id = db.Column('sprite_id', db.INT, nullable=False)

    def __repr__(self):
        return '<Alliance %r>' % self.name
