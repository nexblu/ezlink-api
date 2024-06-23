from flask_bcrypt import Bcrypt
from flask import jsonify
import jwt
from config import REFRESH_TOKEN_KEY, ACCESS_TOKEN_KEY, ALGORITHMS
import datetime


class RefreshTokenController:
    def __init__(self) -> None:
        self.bcrypt = Bcrypt()

    async def refresh_token(self, token):
        if not token or token.isspace():
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "invalid input",
                        "data": {"token": token},
                        "errors": {
                            "token": "token is empety",
                        },
                    }
                ),
                400,
            )
        try:
            decoded_token = jwt.decode(token, REFRESH_TOKEN_KEY, algorithms=ALGORITHMS)
        except:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "token invalid",
                        "data": {"token": token},
                        "errors": None,
                    }
                ),
                400,
            )
        else:
            access_token = jwt.encode(
                {
                    "user_id": decoded_token["user_id"],
                    "username": decoded_token["username"],
                    "email": decoded_token["email"],
                    "is_active": decoded_token["is_active"],
                    "is_admin": decoded_token["is_admin"],
                    "exp": datetime.datetime.now(datetime.timezone.utc).timestamp()
                    + datetime.timedelta(minutes=5).total_seconds(),
                },
                ACCESS_TOKEN_KEY,
                algorithm=ALGORITHMS,
            )
            return (
                jsonify(
                    {
                        "success": True,
                        "status_code": 201,
                        "message": "create new token",
                        "data": {
                            "token": {
                                "access_token": access_token,
                            }
                        },
                        "errors": None,
                    }
                ),
                201,
            )
