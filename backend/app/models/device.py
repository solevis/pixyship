import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.ext.db import db


class Device(db.Model):  # type: ignore[name-defined]
    key: Mapped[str] = mapped_column(primary_key=True)
    checksum: Mapped[str]
    client_datetime: Mapped[datetime.datetime]
    token: Mapped[str | None]
    expires_at: Mapped[datetime.datetime]

    def __repr__(self) -> str:
        return f"<Device {self.key} {self.token} {self.expires_at}>"

    def get_token(self) -> str | None:
        if not self.token or self.expires_at.replace(tzinfo=datetime.UTC) < datetime.datetime.now(tz=datetime.UTC):
            self.cycle_token()

        return self.token

    def cycle_token(self):
        from app.pixelstarshipsapi import PixelStarshipsApi

        pixel_starships_api = PixelStarshipsApi()
        self.token = pixel_starships_api.get_device_token(self.key, self.client_datetime, self.checksum)
        if self.token is not None:
            self.expires_at = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=12)

        db.session.commit()
