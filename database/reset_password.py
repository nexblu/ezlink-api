from .config import db_session, init_db
from models import ResetPasswordDatabase
from .database import Database
from sqlalchemy import func, and_, desc
import datetime
from utils import UserNotFound, EmailAlreadySend


class ResetPasswordCRUD(Database):
    def __init__(self) -> None:
        super().__init__()
        init_db()

    async def insert(self, user_id, token, created_at, expired_at):
        if user_token := (
            ResetPasswordDatabase.query.filter(ResetPasswordDatabase.user_id == user_id)
            .order_by(desc(ResetPasswordDatabase.created_at))
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
        reset_password = ResetPasswordDatabase(
            user_id, token, created_at, created_at, expired_at
        )
        db_session.add(reset_password)
        db_session.commit()
        return reset_password

    async def delete(self, category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            user_token = ResetPasswordDatabase.query.filter(
                ResetPasswordDatabase.user_id == user_id
            ).first()
            db_session.delete(user_token)
            db_session.commit()
            return
        raise UserNotFound

    async def get(self, category, **kwargs):
        email = kwargs.get("email")
        token = kwargs.get("token")
        user_id = kwargs.get("user_id")
        if category == "email":
            return (
                ResetPasswordDatabase.query.filter(
                    func.lower(ResetPasswordDatabase.email) == email.lower()
                )
                .order_by(ResetPasswordDatabase.created_at)
                .first()
            )
        elif category == "token":
            if data := ResetPasswordDatabase.query.filter(
                and_(
                    ResetPasswordDatabase.user_id == user_id,
                    ResetPasswordDatabase.token == token,
                    datetime.datetime.now(datetime.timezone.utc).timestamp()
                    < ResetPasswordDatabase.expired_at,
                )
            ).first():
                return data
            raise UserNotFound

    async def update(self, category, **kwargs):
        pass
