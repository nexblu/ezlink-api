from functools import wraps
from flask import request, abort
import jwt
from config import ACCESS_TOKEN_KEY, ALGORITHMS
import datetime


def token_required():
    def _token_required(f):
        @wraps(f)
        async def __token_required(*args, **kwargs):
            authorization_header = request.headers
            try:
                token = authorization_header["Authorization"].split(" ")[1]
            except:
                abort(401)
            try:
                user_decoded = jwt.decode(
                    token, ACCESS_TOKEN_KEY, algorithms=[ALGORITHMS]
                )
            except jwt.exceptions.DecodeError:
                abort(401)
            except jwt.exceptions.ExpiredSignatureError:
                abort(401)
            else:
                from database import UserCRUD

                user_database = UserCRUD()
                try:
                    user = await user_database.get(
                        "email", email=user_decoded["email"]
                    )
                except:
                    abort(401)
                if not (
                    user.is_active
                    and user.unbanned_at is None
                    and user.banned_at is None
                ):
                    if not user.is_active or user.unbanned_at:
                        try:
                            if (
                                user.unbanned_at
                                < datetime.datetime.now(
                                    datetime.timezone.utc
                                ).timestamp()
                            ):
                                abort(403)
                            else:
                                await user_database.update(
                                    "unbanned", unbanned_at=None, email=user.email
                                )
                        except:
                            abort(403)
                    abort(403)

                request.user = user
                return await f(*args, **kwargs)

        return __token_required

    return _token_required
