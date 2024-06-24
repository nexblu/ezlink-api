from utils import UserNotFound, Validator
from config import API_URL
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import JWTManager
from database import UserCRUD
from flask_bcrypt import Bcrypt
from flask import jsonify, url_for


class LoginController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()
        self.bcrypt = Bcrypt()
        self.jwt = JWTManager()

    async def login(self, email, password):
        if errors := await Validator.validate_login(email, password):
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": 'input invalid',
                        "data": {"email": email, "password": password},
                        'errors': errors,
                    }
                ),
                400,
            )
        try:
            user = await self.user_database.get("email", email=email)
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": 'user not found',
                        "data": {"email": email, "password": password},
                        'errors': None
                    }
                ),
                404,
            )
        else:
            if not user.is_active:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 400,
                            "message": 'user is not active',
                            "data": {
                                "email": email,
                                "username": user.username,
                                "user_id": user.id,
                                "is_active": user.is_active,
                                "created_at": user.created_at,
                                "updated_at": user.updated_at,
                                "banned_at": user.banned_at,
                                "unbanned_at": user.unbanned_at,
                                "profile_image": f'{API_URL}{url_for(
                                    "api user.get_avatar",
                                    user_id=user.id,
                                    profile_name=user.profile_name,
                                )}',
                            },
                            'errors': None
                        }
                    ),
                    400,
                )
            try:
                if self.bcrypt.check_password_hash(user.password, password):
                    access_token = create_access_token(identity=user.id, additional_claims={"username": user.username, "profile_image": f'{API_URL}{url_for(
                                    "api user.get_avatar",
                                    user_id=user.id,
                                    profile_name=user.profile_name,
                                )}'})
                    refresh_token = create_refresh_token(identity=user.id, additional_claims={"username": user.username, "profile_image": f'{API_URL}{url_for(
                                    "api user.get_avatar",
                                    user_id=user.id,
                                    profile_name=user.profile_name,
                                )}'})
                    return (
                        jsonify(
                            {
                                "success": True,
                                "status_code": 200,
                                "message": f"user was found",
                                "data": {
                                    "user_id": user.id,
                                    "username": user.username,
                                    "email": user.email,
                                    "is_active": user.is_active,
                                    "created_at": user.created_at,
                                    "updated_at": user.updated_at,
                                    "banned_at": user.banned_at,
                                    "unbanned_at": user.unbanned_at,
                                    "profile_image": f'{API_URL}{url_for(
                                        "api user.get_avatar",
                                        user_id=user.id,
                                        profile_name=user.profile_name,
                                    )}',
                                    "token": {
                                        "access_token": access_token,
                                        "refresh_token": refresh_token,
                                    },
                                },
                            }
                        ),
                        200,
                    )
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 404,
                            "message": 'user not found',
                            "data": {"email": email, "password": password},
                            'errors': None
                        }
                    ),
                    404,
                )
            except TypeError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 404,
                            "message": "user not found",
                            "data": {"email": email, "password": password},
                            'errors': None
                        }
                    ),
                    404,
                )
