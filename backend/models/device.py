from datetime import datetime, timedelta

from db import db


class Device(db.Model):
    key = db.Column('key', db.TEXT, primary_key=True)
    checksum = db.Column('checksum', db.TEXT, nullable=False)
    token = db.Column('token', db.TEXT)
    expires_at = db.Column('expires_at', db.TEXT)

    def __repr__(self):
        return '<Device {} {} {}>'.format(self.key, self.token, self.expires_at)

    def get_token(self):
        if not self.token or self.expires_at < datetime.now():
            self.cycle_token()

        return self.token

    def cycle_token(self):
        from pixelstarshipsapi import PixelStarshipsApi

        pixel_starships_api = PixelStarshipsApi()
        self.token = pixel_starships_api.get_device_token(self.key, self.checksum)
        self.expires_at = datetime.now() + timedelta(hours=12)

        db.session.commit()
