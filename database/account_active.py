from .config import db_session, init_db
from models import AccountActiveDatabase, UserDatabase
from .database import Database
from sqlalchemy import and_, desc
from utils import UserNotFound, EmailAlreadySend
import datetime


class AccountActiveCRUD(Database):
    def __init__(self) -> None:
        super().__init__()
        init_db()

    async def insert(self, user_id, token, created_at, expired_at):
        if user_token := (
            AccountActiveDatabase.query.filter(AccountActiveDatabase.user_id == user_id)
            .order_by(desc(AccountActiveDatabase.created_at))
            .first()
        ):
            if (
                user_token.expired_at
                < datetime.datetime.now(datetime.timezone.utc).timestamp()
            ):
                user_token.token = token
                user_token.updated_at = datetime.datetime.now(
                    datetime.timezone.utc
                ).timestamp()
                db_session.commit()
                return user_token
            raise EmailAlreadySend
        account_active = AccountActiveDatabase(
            user_id, token, created_at, created_at, expired_at
        )
        db_session.add(account_active)
        db_session.commit()
        return account_active

    async def delete(self, category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user_token := (
                AccountActiveDatabase.query.filter(
                    AccountActiveDatabase.user_id == user_id
                )
                .order_by(desc(AccountActiveDatabase.created_at))
                .first()
            ):
                db_session.delete(user_token)
                db_session.commit()

    async def get(self, category, **kwargs):
        token = kwargs.get("token")
        user_id = kwargs.get("user_id")
        if category == "token":
            if (
                data := db_session.query(UserDatabase, AccountActiveDatabase)
                .select_from(UserDatabase)
                .join(AccountActiveDatabase)
                .filter(
                    and_(
                        AccountActiveDatabase.user_id == user_id,
                        AccountActiveDatabase.token == token,
                        datetime.datetime.now(datetime.timezone.utc).timestamp()
                        < AccountActiveDatabase.expired_at,
                    )
                )
                .order_by(desc(AccountActiveDatabase.created_at))
                .first()
            ):
                return data
            raise UserNotFound

    async def update(self, category, **kwargs):
        pass
