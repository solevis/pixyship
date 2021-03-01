# from run import db
import hashlib
from datetime import datetime, timedelta
from xml.etree import ElementTree

import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class Player(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    name = db.Column('name', db.TEXT, nullable=False)
    trophies = db.Column('trophies', db.INT, nullable=False)
    alliance_id = db.Column('alliance_id', db.INT)
    last_login_at = db.Column('last_login_at', db.TIMESTAMP)

    def __repr__(self):
        return '<User %r>' % self.name


class Alliance(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    name = db.Column('name', db.TEXT, nullable=False)
    sprite_id = db.Column('sprite_id', db.INT, nullable=False)

    def __repr__(self):
        return '<Alliance %r>' % self.name


class Device(db.Model):
    key = db.Column('key', db.TEXT, primary_key=True)
    checksum = db.Column('checksum', db.TEXT, nullable=False)
    token = db.Column('token', db.TEXT)
    expires_at = db.Column('expires_at', db.TEXT)

    def __repr__(self):
        return '<Device {} {} {}>'.format(self.key, self.token, self.expires_at)

    def access_token_param(self):
        if not self.token or self.expires_at < datetime.now():
            self.cycle_token()
        return '&accessToken={token}'.format(token=self.token)

    def cycle_token(self):
        from ps_client import PixelStarshipsApi
        # print('cycling token')
        url = (
            PixelStarshipsApi().server + '/UserService/DeviceLogin8'
            '?deviceKey={}'
            '&isJailBroken=false'
            '&checksum={}'
            '&deviceType=DeviceTypeMac'
            '&languagekey=en'
            '&advertisingKey=%22%22'.format(self.key, self.checksum)
        )

        r = requests.post(url)
        root = ElementTree.fromstring(r.text)
        self.token = root.find('UserLogin').attrib['accessToken']
        self.expires_at = datetime.now() + timedelta(hours=12)
        db.session.commit()


class Listing(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    sale_at = db.Column('sale_at', db.TIMESTAMP, nullable=False)
    item_name = db.Column('item_name', db.TEXT, nullable=False)
    item_id = db.Column('item_id', db.INT, nullable=False)
    amount = db.Column('amount', db.INT, nullable=False)
    currency = db.Column('currency', db.TEXT, nullable=False)
    price = db.Column('price', db.INT, nullable=False)
    user_id = db.Column('user_id', db.INT, nullable=False)


class Record(db.Model):
    id = db.Column('id', db.INT, primary_key=True)
    type = db.Column('type', db.TEXT, nullable=False)
    type_id = db.Column('type_id', db.INT, nullable=False)
    current = db.Column('current', db.BOOLEAN, nullable=False)
    md5_hash = db.Column('md5_hash', UUID, nullable=False)
    data = db.Column('data', db.TEXT, nullable=False)
    created_at = db.Column('created_at', db.TIMESTAMP, server_default=func.now())

    @classmethod
    def update_data(cls, type_str, type_id, element, ignore_list=None):
        """Save a record to the DB with hash"""
        ignore_list = ignore_list or []

        data_str = ElementTree.tostring(element).decode()

        # Ignore some fields for hashing
        for i in ignore_list:
            element.attrib.pop(i, None)
        md5_str = ElementTree.tostring(element).decode()
        md5 = hashlib.md5(md5_str.encode('utf-8')).hexdigest()

        # Check if this is already in the db as the current
        existing = Record.query.filter_by(type=type_str, type_id=type_id, current=True).first()

        if existing:
            if existing.md5_hash.replace('-', '') == md5:
                # If we ignored fields, update them, but don't make a new record.
                if ignore_list:
                    if existing.data != data_str:
                        existing.data = data_str
                        db.session.commit()
                return
            else:
                existing.current = False

        r = cls(
            type=type_str,
            type_id=type_id,
            current=True,
            md5_hash=md5,
            data=data_str,
        )
        db.session.add(r)
        db.session.commit()
