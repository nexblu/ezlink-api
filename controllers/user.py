from database import UserCRUD
from flask import send_file, jsonify, url_for
from io import BytesIO
from utils import UserNotFound
from flask_jwt_extended import current_user
from config import API_URL


class UserController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()

    async def get_me(self):
        return (
            jsonify(
                {
                    "success": True,
                    "status_code": 200,
                    "message": "user is valid",
                    "data": {
                        "user_id": current_user.id,
                        "username": current_user.username,
                        "email": current_user.email,
                        "is_active": current_user.is_active,
                        "created_at": current_user.created_at,
                        "updated_at": current_user.updated_at,
                        "banned_at": current_user.banned_at,
                        "unbanned_at": current_user.unbanned_at,
                        "profile_image": f'{API_URL}{url_for(
                                        "api user.get_avatar",
                                        user_id=current_user.id,
                                        profile_name=current_user.profile_name,
                                    )}',
                    },
                    "errors": None,
                }
            ),
            200,
        )

    async def get_avatar(self, user_id, profile_name):
        try:
            user = await self.user_database.get(
                "avatar", user_id=user_id, profile_name=profile_name
            )
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "avatar not found",
                        "data": {"user_id": user_id, "profile_name": profile_name},
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            return send_file(
                BytesIO(user.profile_image),
                mimetype="image/jpeg",
                download_name=f"{profile_name}.jpg",
            )
