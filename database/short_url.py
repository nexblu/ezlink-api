from .config import db_session, init_db
from models import ShortURLDatabase
from .database import Database
from sqlalchemy import desc
from utils import ShortURLNotFound, ShortURLNotAvaible


class ShortURLCRUD(Database):
    def __init__(self) -> None:
        super().__init__()
        init_db()

    async def insert(self, user_id, url, uuid, created_at, aliases=None):
        if short_url := (
            ShortURLDatabase.query.filter(ShortURLDatabase.url == url)
            .order_by(desc(ShortURLDatabase.created_at))
            .first()
        ):
            raise ShortURLNotAvaible
        short_url_data = ShortURLDatabase(user_id, url, uuid, created_at)
        if aliases:
            short_url_data.aliases = aliases
        db_session.add(short_url_data)
        db_session.commit()
        return short_url_data

    async def delete(self, category, **kwargs):
        pass

    async def get(self, category, **kwargs):
        uuid = kwargs.get("uuid")
        user_id = kwargs.get("user_id")
        if category == "uuid":
            if short_url := (
                ShortURLDatabase.query.filter(ShortURLDatabase.uuid == uuid)
                .order_by(desc(ShortURLDatabase.created_at))
                .first()
            ):
                return short_url
            raise ShortURLNotFound
        elif category == "user":
            if short_url := (
                ShortURLDatabase.query.filter(ShortURLDatabase.user_id == user_id)
                .order_by(desc(ShortURLDatabase.created_at))
                .all()
            ):
                return short_url
            raise ShortURLNotFound

    async def update(self, category, **kwargs):
        pass
